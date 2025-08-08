#!/usr/bin/env python3
"""
End-to-End Test Suite for BuildingOS New Architecture
Tests complete mission flow: Persona → Director → Coordinator → Executor Agents

Flow tested:
1. User intention → Persona Agent
2. Persona → Director Agent
3. Director → Coordinator Agent
4. Coordinator → Elevator/PSIM Agents
5. Results flow back through the chain
"""

import json
import boto3
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional


class BuildingOSE2ETest:
    def __init__(self):
        self.sns = boto3.client("sns")
        self.lambda_client = boto3.client("lambda")
        self.dynamodb = boto3.resource("dynamodb")

        # Get topics from Terraform outputs
        self.topics = self._get_topic_arns()
        self.test_mission_id = f"e2e-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"

        print(f"🚀 Starting E2E Test with Mission ID: {self.test_mission_id}")

    def _get_topic_arns(self) -> Dict[str, str]:
        """Get SNS topic ARNs from AWS"""
        topics = {}
        response = self.sns.list_topics()

        for topic in response["Topics"]:
            topic_arn = topic["TopicArn"]
            topic_name = topic_arn.split(":")[-1]

            # Map topic names to our standard names
            if "persona-intention" in topic_name:
                topics["persona_intention"] = topic_arn
            elif "director-mission" in topic_name:
                topics["director_mission"] = topic_arn
            elif "director-response" in topic_name:
                topics["director_response"] = topic_arn
            elif "coordinator-task" in topic_name:
                topics["coordinator_task"] = topic_arn
            elif "agent-task-result" in topic_name:
                topics["agent_task_result"] = topic_arn
            elif "coordinator-mission-result" in topic_name:
                topics["coordinator_mission_result"] = topic_arn

        return topics

    def test_1_user_intention_to_persona(self) -> bool:
        """Test 1: User sends intention to Persona Agent"""
        print("\n📝 Test 1: User Intention → Persona Agent")

        user_intention = {
            "mission_id": self.test_mission_id,
            "user_id": "test-user-001",
            "intention": "Chamar elevador para o 5º andar e depois ir para o térreo",
            "timestamp": datetime.now().isoformat(),
            "context": {
                "current_floor": 5,
                "destination_floor": 0,
                "building_id": "building-001",
                "urgency": "normal",
            },
            "test_mode": True,
        }

        try:
            response = self.sns.publish(
                TopicArn=self.topics["persona_intention"],
                Message=json.dumps(user_intention),
                Subject=f"E2E Test - User Intention {self.test_mission_id}",
            )

            print(f"  ✅ Published to Persona: Message ID {response['MessageId']}")
            print(f"  📋 Intention: {user_intention['intention']}")
            return True

        except Exception as e:
            print(f"  ❌ Failed to publish intention: {e}")
            return False

    def test_2_invoke_persona_agent(self) -> Optional[Dict]:
        """Test 2: Directly invoke Persona Agent to process intention"""
        print("\n🤖 Test 2: Invoke Persona Agent")

        sns_event = {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {
                                "mission_id": self.test_mission_id,
                                "user_id": "test-user-001",
                                "intention": "Chamar elevador para o 5º andar e depois ir para o térreo",
                                "timestamp": datetime.now().isoformat(),
                                "context": {
                                    "current_floor": 5,
                                    "destination_floor": 0,
                                    "building_id": "building-001",
                                    "urgency": "normal",
                                },
                                "test_mode": True,
                            }
                        )
                    }
                }
            ]
        }

        try:
            response = self.lambda_client.invoke(
                FunctionName="bos-agent-persona-dev",
                Payload=json.dumps(sns_event),
                InvocationType="RequestResponse",
            )

            result = json.loads(response["Payload"].read())
            print(f"  ✅ Persona Agent Response: {result.get('statusCode', 'Unknown')}")

            if response.get("FunctionError"):
                print(f"  ⚠️  Function Error: {response['FunctionError']}")
                return None

            return result

        except Exception as e:
            print(f"  ❌ Failed to invoke Persona Agent: {e}")
            return None

    def test_3_check_director_mission(self) -> bool:
        """Test 3: Check if Director received and processed mission"""
        print("\n🎯 Test 3: Director Mission Processing")

        # Wait a bit for async processing
        print("  ⏳ Waiting for Director processing...")
        time.sleep(3)

        # Try to invoke Director with a sample mission
        director_event = {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {
                                "mission_id": self.test_mission_id,
                                "user_intention": "Chamar elevador para o 5º andar e depois ir para o térreo",
                                "context": {
                                    "current_floor": 5,
                                    "destination_floor": 0,
                                    "building_id": "building-001",
                                },
                                "test_mode": True,
                            }
                        )
                    }
                }
            ]
        }

        try:
            response = self.lambda_client.invoke(
                FunctionName="bos-agent-director-dev",
                Payload=json.dumps(director_event),
                InvocationType="RequestResponse",
            )

            result = json.loads(response["Payload"].read())
            print(
                f"  ✅ Director Agent Response: {result.get('statusCode', 'Unknown')}"
            )

            if "mission_plan" in str(result):
                print("  📋 Mission plan generated successfully")
                return True
            else:
                print("  ⚠️  No mission plan found in response")
                return False

        except Exception as e:
            print(f"  ❌ Failed to invoke Director Agent: {e}")
            return False

    def test_4_coordinator_task_distribution(self) -> bool:
        """Test 4: Coordinator receives mission and distributes tasks"""
        print("\n📊 Test 4: Coordinator Task Distribution")

        coordinator_event = {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {
                                "mission_id": self.test_mission_id,
                                "mission_plan": {
                                    "tasks": [
                                        {
                                            "task_id": f"task-001-{self.test_mission_id}",
                                            "agent": "agent_elevator",
                                            "action": "call_elevator",
                                            "parameters": {
                                                "floor": 5,
                                                "direction": "down",
                                            },
                                        }
                                    ]
                                },
                                "test_mode": True,
                            }
                        )
                    }
                }
            ]
        }

        try:
            response = self.lambda_client.invoke(
                FunctionName="bos-agent-coordinator-dev",
                Payload=json.dumps(coordinator_event),
                InvocationType="RequestResponse",
            )

            result = json.loads(response["Payload"].read())
            print(
                f"  ✅ Coordinator Agent Response: {result.get('statusCode', 'Unknown')}"
            )

            if "task" in str(result).lower():
                print("  📋 Tasks distributed successfully")
                return True
            else:
                print("  ⚠️  Task distribution unclear")
                return False

        except Exception as e:
            print(f"  ❌ Failed to invoke Coordinator Agent: {e}")
            return False

    def test_5_elevator_agent_execution(self) -> bool:
        """Test 5: Elevator Agent executes task"""
        print("\n🛗 Test 5: Elevator Agent Execution")

        elevator_event = {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {
                                "mission_id": self.test_mission_id,
                                "task_id": f"task-001-{self.test_mission_id}",
                                "agent": "agent_elevator",
                                "action": "call_elevator",
                                "parameters": {"floor": 5, "direction": "down"},
                                "test_mode": True,
                            }
                        )
                    }
                }
            ]
        }

        try:
            response = self.lambda_client.invoke(
                FunctionName="bos-agent-elevator-dev",
                Payload=json.dumps(elevator_event),
                InvocationType="RequestResponse",
            )

            result = json.loads(response["Payload"].read())
            print(
                f"  ✅ Elevator Agent Response: {result.get('statusCode', 'Unknown')}"
            )

            # Check if response indicates successful task handling
            if result.get("statusCode") == 200 or "success" in str(result).lower():
                print("  🛗 Elevator task executed successfully")
                return True
            else:
                print("  ⚠️  Elevator task execution unclear")
                return False

        except Exception as e:
            print(f"  ❌ Failed to invoke Elevator Agent: {e}")
            return False

    def test_6_psim_agent_execution(self) -> bool:
        """Test 6: PSIM Agent executes access control task"""
        print("\n🔐 Test 6: PSIM Agent Execution")

        psim_event = {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {
                                "mission_id": self.test_mission_id,
                                "task_id": f"task-002-{self.test_mission_id}",
                                "agent": "agent_psim",
                                "action": "check_access",
                                "parameters": {
                                    "user_id": "test-user-001",
                                    "floor": 5,
                                    "action": "access_floor",
                                },
                                "test_mode": True,
                            }
                        )
                    }
                }
            ]
        }

        try:
            response = self.lambda_client.invoke(
                FunctionName="bos-agent-psim-dev",
                Payload=json.dumps(psim_event),
                InvocationType="RequestResponse",
            )

            result = json.loads(response["Payload"].read())
            print(f"  ✅ PSIM Agent Response: {result.get('statusCode', 'Unknown')}")

            if result.get("statusCode") == 200 or "success" in str(result).lower():
                print("  🔐 PSIM task executed successfully")
                return True
            else:
                print("  ⚠️  PSIM task execution unclear")
                return False

        except Exception as e:
            print(f"  ❌ Failed to invoke PSIM Agent: {e}")
            return False

    def test_7_sns_topic_connectivity(self) -> Dict[str, bool]:
        """Test 7: Verify all SNS topics are properly connected"""
        print("\n📡 Test 7: SNS Topic Connectivity")

        results = {}

        for topic_name, topic_arn in self.topics.items():
            try:
                # Test publish capability
                test_message = {
                    "test_type": "connectivity_test",
                    "mission_id": self.test_mission_id,
                    "timestamp": datetime.now().isoformat(),
                    "topic": topic_name,
                }

                response = self.sns.publish(
                    TopicArn=topic_arn,
                    Message=json.dumps(test_message),
                    Subject=f"E2E Connectivity Test - {topic_name}",
                )

                results[topic_name] = True
                print(
                    f"  ✅ {topic_name}: Connected (Message ID: {response['MessageId'][:8]}...)"
                )

            except Exception as e:
                results[topic_name] = False
                print(f"  ❌ {topic_name}: Failed - {e}")

        return results

    def test_8_architecture_validation(self) -> Dict[str, any]:
        """Test 8: Validate new architecture completeness"""
        print("\n🏗️  Test 8: Architecture Validation")

        expected_topics = [
            "persona_intention",
            "director_mission",
            "director_response",
            "coordinator_task",
            "agent_task_result",
            "coordinator_mission_result",
        ]

        validation_results = {
            "topics_present": [],
            "topics_missing": [],
            "lambda_functions": {},
            "architecture_score": 0,
        }

        # Check topics
        for topic in expected_topics:
            if topic in self.topics:
                validation_results["topics_present"].append(topic)
                print(f"  ✅ Topic: {topic}")
            else:
                validation_results["topics_missing"].append(topic)
                print(f"  ❌ Missing: {topic}")

        # Check Lambda functions
        functions_to_check = [
            "bos-agent-persona-dev",
            "bos-agent-director-dev",
            "bos-agent-coordinator-dev",
            "bos-agent-elevator-dev",
            "bos-agent-psim-dev",
        ]

        for func_name in functions_to_check:
            try:
                response = self.lambda_client.get_function(FunctionName=func_name)
                validation_results["lambda_functions"][func_name] = {
                    "exists": True,
                    "runtime": response["Configuration"]["Runtime"],
                    "last_modified": response["Configuration"]["LastModified"],
                }
                print(f"  ✅ Function: {func_name}")
            except Exception as e:
                validation_results["lambda_functions"][func_name] = {
                    "exists": False,
                    "error": str(e),
                }
                print(f"  ❌ Function: {func_name} - {e}")

        # Calculate architecture score
        topics_score = (
            len(validation_results["topics_present"]) / len(expected_topics) * 50
        )
        functions_score = (
            sum(
                1
                for f in validation_results["lambda_functions"].values()
                if f.get("exists")
            )
            / len(functions_to_check)
            * 50
        )
        validation_results["architecture_score"] = round(
            topics_score + functions_score, 2
        )

        print(
            f"  📊 Architecture Score: {validation_results['architecture_score']}/100"
        )

        return validation_results

    def run_complete_e2e_test(self) -> Dict[str, any]:
        """Run the complete end-to-end test suite"""
        print("=" * 80)
        print("🧪 BUILDINGOS E2E TEST SUITE - NEW ARCHITECTURE")
        print("=" * 80)
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🆔 Mission ID: {self.test_mission_id}")
        print(f"🏗️  Architecture: New Standardized SNS Topics")

        test_results = {
            "mission_id": self.test_mission_id,
            "start_time": datetime.now().isoformat(),
            "tests": {},
        }

        # Run all tests
        test_results["tests"][
            "1_user_intention"
        ] = self.test_1_user_intention_to_persona()
        test_results["tests"]["2_persona_agent"] = (
            self.test_2_invoke_persona_agent() is not None
        )
        test_results["tests"][
            "3_director_mission"
        ] = self.test_3_check_director_mission()
        test_results["tests"][
            "4_coordinator_tasks"
        ] = self.test_4_coordinator_task_distribution()
        test_results["tests"][
            "5_elevator_execution"
        ] = self.test_5_elevator_agent_execution()
        test_results["tests"]["6_psim_execution"] = self.test_6_psim_agent_execution()

        # Connectivity and validation tests
        test_results["tests"][
            "7_sns_connectivity"
        ] = self.test_7_sns_topic_connectivity()
        test_results["tests"][
            "8_architecture_validation"
        ] = self.test_8_architecture_validation()

        test_results["end_time"] = datetime.now().isoformat()

        # Generate summary
        self._generate_test_summary(test_results)

        return test_results

    def _generate_test_summary(self, results: Dict) -> None:
        """Generate and display test summary"""
        print("\n" + "=" * 80)
        print("📊 E2E TEST SUMMARY")
        print("=" * 80)

        # Count passed tests
        basic_tests = [
            k
            for k, v in results["tests"].items()
            if k.startswith(("1_", "2_", "3_", "4_", "5_", "6_"))
            and isinstance(v, bool)
        ]
        passed_basic = sum(1 for k in basic_tests if results["tests"][k])

        # SNS connectivity
        sns_results = results["tests"]["7_sns_connectivity"]
        sns_passed = sum(1 for v in sns_results.values() if v)
        sns_total = len(sns_results)

        # Architecture validation
        arch_results = results["tests"]["8_architecture_validation"]
        arch_score = arch_results["architecture_score"]

        print(f"🧪 Basic Flow Tests: {passed_basic}/{len(basic_tests)} PASSED")
        print(f"📡 SNS Connectivity: {sns_passed}/{sns_total} TOPICS")
        print(f"🏗️  Architecture Score: {arch_score}/100")

        # Overall status
        overall_success = (
            passed_basic >= len(basic_tests) * 0.8  # 80% basic tests pass
            and sns_passed >= sns_total * 0.8  # 80% SNS topics work
            and arch_score >= 80  # 80% architecture score
        )

        status = "✅ READY FOR PRODUCTION" if overall_success else "⚠️  NEEDS ATTENTION"
        print(f"\n🎯 Overall Status: {status}")

        if not overall_success:
            print("\n📋 RECOMMENDED ACTIONS:")
            if passed_basic < len(basic_tests) * 0.8:
                print("  - Review agent configurations and SNS subscriptions")
            if sns_passed < sns_total * 0.8:
                print("  - Check SNS topic permissions and Lambda triggers")
            if arch_score < 80:
                print("  - Verify all required resources are deployed")


if __name__ == "__main__":
    try:
        tester = BuildingOSE2ETest()
        results = tester.run_complete_e2e_test()

        # Save results to file
        with open(
            f"e2e_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w"
        ) as f:
            json.dump(results, f, indent=2, default=str)

    except Exception as e:
        print(f"❌ E2E Test Suite failed to start: {e}")
        exit(1)

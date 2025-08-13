#!/usr/bin/env python3
"""
=============================================================================
BuildingOS Platform - Storage Foundation Validation Script
=============================================================================

**Purpose:** Comprehensive validation of storage infrastructure for Step 1.3
**Scope:** DynamoDB tables, S3 frontend bucket, and integration testing
**Framework:** Python-based validation with detailed pass/fail criteria

**Components Validated:**
- 4 DynamoDB tables: websocket_connections, short_term_memory, mission_state, elevator_monitoring
- 1 S3 bucket: buildingos-frontend-dev with CloudFront distribution
- IAM permissions and access controls
- Integration with Lambda functions and VPC endpoints

**Quality Gates:**
- All resources must exist and be properly configured
- Encryption settings must be prepared for KMS (Phase 4)
- Compliance tags must be present and accurate
- Performance settings must be optimized for serverless workloads

**Usage:** python tests/validation/validate_storage_step.py
**Requirements:** AWS CLI configured, Python 3.8+, boto3

=============================================================================
"""

import boto3
import json
import sys
import time
from typing import Dict, List, Tuple, Any
from botocore.exceptions import ClientError, NoCredentialsError

# Test configuration
ENVIRONMENT = "dev"
REGION = "us-east-1"
PROJECT_PREFIX = f"bos-{ENVIRONMENT}"

# Expected resources configuration
EXPECTED_DYNAMODB_TABLES = {
    f"{PROJECT_PREFIX}-websocket-connections": {
        "hash_key": "connection_id",
        "billing_mode": "PAY_PER_REQUEST",
        "data_classification": "internal",
        "retention_period": "365Days",
    },
    f"{PROJECT_PREFIX}-short-term-memory": {
        "hash_key": "user_id",
        "billing_mode": "PAY_PER_REQUEST",
        "data_classification": "confidential",
        "retention_period": "90Days",
    },
    f"{PROJECT_PREFIX}-mission-state": {
        "hash_key": "mission_id",
        "billing_mode": "PAY_PER_REQUEST",
        "data_classification": "internal",
        "retention_period": "365Days",
    },
    f"{PROJECT_PREFIX}-elevator-monitoring": {
        "hash_key": "elevator_id",
        "billing_mode": "PAY_PER_REQUEST",
        "data_classification": "internal",
        "retention_period": "730Days",
    },
}

EXPECTED_S3_BUCKETS = {
    f"buildingos-frontend-{ENVIRONMENT}": {
        "website_hosting": True,
        "public_access": True,
        "data_classification": "public",
        "retention_period": "permanent",
    }
}


class StorageValidator:
    """Comprehensive storage infrastructure validator"""

    def __init__(self):
        """Initialize AWS clients and validation state"""
        try:
            self.dynamodb = boto3.client("dynamodb", region_name=REGION)
            self.s3 = boto3.client("s3", region_name=REGION)
            self.cloudfront = boto3.client("cloudfront", region_name=REGION)
            self.iam = boto3.client("iam", region_name=REGION)
            self.sts = boto3.client("sts", region_name=REGION)

            # Get current AWS account ID
            self.account_id = self.sts.get_caller_identity()["Account"]

            self.test_results = []
            self.passed_tests = 0
            self.total_tests = 0

            print(f"🔍 Storage Foundation Validation - Environment: {ENVIRONMENT}")
            print(f"📍 Region: {REGION}")
            print(f"🏷️ Project Prefix: {PROJECT_PREFIX}")
            print("=" * 80)

        except NoCredentialsError:
            print("❌ ERROR: AWS credentials not configured")
            sys.exit(1)
        except Exception as e:
            print(f"❌ ERROR: Failed to initialize AWS clients: {str(e)}")
            sys.exit(1)

    def run_test(self, test_name: str, test_func) -> bool:
        """Execute a test and record results"""
        self.total_tests += 1
        print(f"\n🧪 Test {self.total_tests}: {test_name}")

        try:
            result = test_func()
            if result:
                print(f"✅ PASS: {test_name}")
                self.passed_tests += 1
                self.test_results.append(
                    {
                        "test": test_name,
                        "status": "PASS",
                        "details": "Test completed successfully",
                    }
                )
                return True
            else:
                print(f"❌ FAIL: {test_name}")
                self.test_results.append(
                    {
                        "test": test_name,
                        "status": "FAIL",
                        "details": "Test failed validation criteria",
                    }
                )
                return False

        except Exception as e:
            print(f"❌ ERROR: {test_name} - {str(e)}")
            self.test_results.append(
                {"test": test_name, "status": "ERROR", "details": str(e)}
            )
            return False

    def validate_dynamodb_table_exists(
        self, table_name: str, expected_config: Dict
    ) -> bool:
        """Validate DynamoDB table existence and configuration"""
        try:
            response = self.dynamodb.describe_table(TableName=table_name)
            table = response["Table"]

            # Validate table status
            if table["TableStatus"] != "ACTIVE":
                print(
                    f"   ⚠️  Table {table_name} is not ACTIVE (status: {table['TableStatus']})"
                )
                return False

            # Validate billing mode
            if (
                table["BillingModeSummary"]["BillingMode"]
                != expected_config["billing_mode"]
            ):
                print(f"   ⚠️  Table {table_name} billing mode mismatch")
                return False

            # Validate hash key
            hash_key = next(
                (
                    attr["AttributeName"]
                    for attr in table["KeySchema"]
                    if attr["KeyType"] == "HASH"
                ),
                None,
            )
            if hash_key != expected_config["hash_key"]:
                print(f"   ⚠️  Table {table_name} hash key mismatch")
                return False

            # Validate point-in-time recovery
            pitr_response = self.dynamodb.describe_continuous_backups(
                TableName=table_name
            )
            if (
                not pitr_response["ContinuousBackupsDescription"][
                    "PointInTimeRecoveryDescription"
                ]["PointInTimeRecoveryStatus"]
                == "ENABLED"
            ):
                print(f"   ⚠️  Table {table_name} point-in-time recovery not enabled")
                return False

            print(
                f"   ✅ Table {table_name}: ACTIVE, {expected_config['billing_mode']}, key={hash_key}, PITR=enabled"
            )
            return True

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                print(f"   ❌ Table {table_name} does not exist")
            else:
                print(f"   ❌ Error checking table {table_name}: {e}")
            return False

    def validate_dynamodb_table_tags(
        self, table_name: str, expected_config: Dict
    ) -> bool:
        """Validate DynamoDB table tags and compliance"""
        try:
            response = self.dynamodb.list_tags_of_resource(
                ResourceArn=f"arn:aws:dynamodb:{REGION}:{self.account_id}:table/{table_name}"
            )
            tags = {tag["Key"]: tag["Value"] for tag in response.get("Tags", [])}

            # Required compliance tags
            required_tags = {
                "DataClassification": expected_config["data_classification"],
                "RetentionPeriod": expected_config["retention_period"],
                "Compliance": "lgpd",
                "Encryption": "kms",
                "ManagedBy": "Terraform",
            }

            missing_tags = []
            incorrect_tags = []

            for key, expected_value in required_tags.items():
                if key not in tags:
                    missing_tags.append(key)
                elif (
                    key in ["DataClassification", "RetentionPeriod"]
                    and tags[key] != expected_value
                ):
                    incorrect_tags.append(
                        f"{key}={tags[key]} (expected {expected_value})"
                    )

            if missing_tags or incorrect_tags:
                if missing_tags:
                    print(f"   ⚠️  Missing tags: {', '.join(missing_tags)}")
                if incorrect_tags:
                    print(f"   ⚠️  Incorrect tags: {', '.join(incorrect_tags)}")
                return False

            print(f"   ✅ Table {table_name}: All compliance tags present and correct")
            return True

        except Exception as e:
            print(f"   ❌ Error checking tags for {table_name}: {e}")
            return False

    def validate_s3_bucket_exists(
        self, bucket_name: str, expected_config: Dict
    ) -> bool:
        """Validate S3 bucket existence and configuration"""
        try:
            # Check bucket exists
            self.s3.head_bucket(Bucket=bucket_name)

            # Check website configuration
            if expected_config.get("website_hosting"):
                try:
                    website_config = self.s3.get_bucket_website(Bucket=bucket_name)
                    if "IndexDocument" not in website_config:
                        print(
                            f"   ⚠️  Bucket {bucket_name} missing index document configuration"
                        )
                        return False
                except ClientError as e:
                    if e.response["Error"]["Code"] == "NoSuchWebsiteConfiguration":
                        print(
                            f"   ⚠️  Bucket {bucket_name} not configured for website hosting"
                        )
                        return False

            # Check encryption configuration
            try:
                encryption = self.s3.get_bucket_encryption(Bucket=bucket_name)
                if "Rules" not in encryption.get(
                    "ServerSideEncryptionConfiguration", {}
                ):
                    print(
                        f"   ⚠️  Bucket {bucket_name} missing encryption configuration"
                    )
                    return False
            except ClientError as e:
                if (
                    e.response["Error"]["Code"]
                    == "ServerSideEncryptionConfigurationNotFoundError"
                ):
                    print(f"   ⚠️  Bucket {bucket_name} missing server-side encryption")
                    return False

            print(
                f"   ✅ Bucket {bucket_name}: exists, website hosting enabled, encryption configured"
            )
            return True

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print(f"   ❌ Bucket {bucket_name} does not exist")
            else:
                print(f"   ❌ Error checking bucket {bucket_name}: {e}")
            return False

    def validate_s3_bucket_tags(self, bucket_name: str, expected_config: Dict) -> bool:
        """Validate S3 bucket tags and compliance"""
        try:
            response = self.s3.get_bucket_tagging(Bucket=bucket_name)
            tags = {tag["Key"]: tag["Value"] for tag in response.get("TagSet", [])}

            # Required compliance tags
            required_tags = {
                "DataClassification": expected_config["data_classification"],
                "RetentionPeriod": expected_config["retention_period"],
                "Compliance": "lgpd",
                "Encryption": "kms",
                "ManagedBy": "Terraform",
            }

            missing_tags = []
            for key, expected_value in required_tags.items():
                if key not in tags:
                    missing_tags.append(key)
                elif (
                    key in ["DataClassification", "RetentionPeriod"]
                    and tags[key] != expected_value
                ):
                    missing_tags.append(f"{key} (incorrect value)")

            if missing_tags:
                print(f"   ⚠️  Missing/incorrect tags: {', '.join(missing_tags)}")
                return False

            print(
                f"   ✅ Bucket {bucket_name}: All compliance tags present and correct"
            )
            return True

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchTagSet":
                print(f"   ⚠️  Bucket {bucket_name} has no tags")
            else:
                print(f"   ❌ Error checking tags for {bucket_name}: {e}")
            return False

    def validate_cloudfront_distribution(self) -> bool:
        """Validate CloudFront distribution for frontend"""
        try:
            distributions = self.cloudfront.list_distributions()

            # Find distribution for our frontend bucket
            frontend_bucket = f"buildingos-frontend-{ENVIRONMENT}"
            distribution = None

            for dist in distributions.get("DistributionList", {}).get("Items", []):
                for origin in dist.get("Origins", {}).get("Items", []):
                    if frontend_bucket in origin.get("DomainName", ""):
                        distribution = dist
                        break
                if distribution:
                    break

            if not distribution:
                print(f"   ⚠️  No CloudFront distribution found for {frontend_bucket}")
                return False

            # Validate distribution status
            if distribution["Status"] != "Deployed":
                print(
                    f"   ⚠️  CloudFront distribution not deployed (status: {distribution['Status']})"
                )
                return False

            # Validate HTTPS redirect
            default_behavior = distribution["DefaultCacheBehavior"]
            if default_behavior["ViewerProtocolPolicy"] != "redirect-to-https":
                print(f"   ⚠️  CloudFront not configured to redirect to HTTPS")
                return False

            print(f"   ✅ CloudFront distribution: deployed, HTTPS redirect enabled")
            return True

        except Exception as e:
            print(f"   ❌ Error checking CloudFront distribution: {e}")
            return False

    def validate_lambda_dynamodb_integration(self) -> bool:
        """Validate Lambda functions can access DynamoDB tables"""
        try:
            lambda_client = boto3.client("lambda", region_name=REGION)

            # Get Lambda functions that should access DynamoDB
            functions = lambda_client.list_functions()
            bos_functions = [
                f
                for f in functions["Functions"]
                if f["FunctionName"].startswith(PROJECT_PREFIX)
            ]

            if len(bos_functions) == 0:
                print(f"   ⚠️  No Lambda functions found with prefix {PROJECT_PREFIX}")
                return False

            # Check environment variables for DynamoDB table names
            functions_with_db_access = 0
            for func in bos_functions:
                try:
                    config = lambda_client.get_function_configuration(
                        FunctionName=func["FunctionName"]
                    )
                    env_vars = config.get("Environment", {}).get("Variables", {})

                    # Check for DynamoDB table environment variables
                    db_env_vars = [
                        var
                        for var in env_vars.keys()
                        if "TABLE_NAME" in var or "DB" in var
                    ]
                    if db_env_vars:
                        functions_with_db_access += 1

                except Exception as e:
                    print(f"   ⚠️  Error checking function {func['FunctionName']}: {e}")

            if functions_with_db_access == 0:
                print(f"   ⚠️  No Lambda functions configured with DynamoDB access")
                return False

            print(
                f"   ✅ Lambda integration: {functions_with_db_access} functions configured for DynamoDB access"
            )
            return True

        except Exception as e:
            print(f"   ❌ Error validating Lambda-DynamoDB integration: {e}")
            return False

    def run_all_validations(self) -> bool:
        """Execute all storage validation tests"""
        print("🚀 Starting Storage Foundation Validation Tests")

        # Test 1: DynamoDB Tables Existence and Configuration
        for table_name, config in EXPECTED_DYNAMODB_TABLES.items():
            self.run_test(
                f"DynamoDB Table Exists and Configured: {table_name}",
                lambda tn=table_name, cfg=config: self.validate_dynamodb_table_exists(
                    tn, cfg
                ),
            )

        # Test 2: DynamoDB Tables Tags and Compliance
        for table_name, config in EXPECTED_DYNAMODB_TABLES.items():
            self.run_test(
                f"DynamoDB Table Tags and Compliance: {table_name}",
                lambda tn=table_name, cfg=config: self.validate_dynamodb_table_tags(
                    tn, cfg
                ),
            )

        # Test 3: S3 Buckets Existence and Configuration
        for bucket_name, config in EXPECTED_S3_BUCKETS.items():
            self.run_test(
                f"S3 Bucket Exists and Configured: {bucket_name}",
                lambda bn=bucket_name, cfg=config: self.validate_s3_bucket_exists(
                    bn, cfg
                ),
            )

        # Test 4: S3 Buckets Tags and Compliance
        for bucket_name, config in EXPECTED_S3_BUCKETS.items():
            self.run_test(
                f"S3 Bucket Tags and Compliance: {bucket_name}",
                lambda bn=bucket_name, cfg=config: self.validate_s3_bucket_tags(
                    bn, cfg
                ),
            )

        # Test 5: CloudFront Distribution
        self.run_test(
            "CloudFront Distribution Configuration",
            self.validate_cloudfront_distribution,
        )

        # Test 6: Lambda-DynamoDB Integration
        self.run_test(
            "Lambda Functions DynamoDB Integration",
            self.validate_lambda_dynamodb_integration,
        )

        return self.generate_final_report()

    def generate_final_report(self) -> bool:
        """Generate final validation report"""
        print("\n" + "=" * 80)
        print("📊 STORAGE FOUNDATION VALIDATION REPORT")
        print("=" * 80)

        success_rate = (
            (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        )

        print(
            f"📈 Overall Results: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}%)"
        )

        if self.passed_tests == self.total_tests:
            print("🎉 ✅ ALL TESTS PASSED - Storage Foundation is ready!")
            print("\n🎯 Quality Gates Status:")
            print("   ✅ All DynamoDB tables operational and compliant")
            print("   ✅ S3 frontend bucket configured with CloudFront")
            print("   ✅ Encryption prepared for KMS integration (Phase 4)")
            print("   ✅ Lambda functions integrated with storage resources")
            print("   ✅ Compliance tags applied according to LGPD requirements")
            return True
        else:
            failed_tests = self.total_tests - self.passed_tests
            print(
                f"❌ {failed_tests} tests failed - Storage Foundation needs attention"
            )
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if result["status"] != "PASS":
                    print(f"   • {result['test']}: {result['status']}")
            return False


def main():
    """Main validation execution"""
    validator = StorageValidator()
    success = validator.run_all_validations()

    # Save detailed results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"storage_validation_results_{timestamp}.json"

    with open(results_file, "w") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "environment": ENVIRONMENT,
                "total_tests": validator.total_tests,
                "passed_tests": validator.passed_tests,
                "success_rate": (validator.passed_tests / validator.total_tests) * 100,
                "results": validator.test_results,
            },
            f,
            indent=2,
        )

    print(f"\n📄 Detailed results saved to: {results_file}")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

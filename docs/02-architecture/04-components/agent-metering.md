---
status: "Defined"
category: "Agent"
last_updated: "2025-08-06"
owner: "Jomil"
dependencies:
  - "External: Metering System APIs"
  - "AWS: DynamoDB (Shared Memory)"
  - "Internal: agent_erp (via Coordinator)"
source_code: "src/agents/agent_metering/"
---

# Agent: Metering

## 1. Purpose

The Metering Agent is responsible for integrating with automated utility measurement systems (e.g., for water and gas). Its purpose is to collect consumption data, store it for historical analysis, and trigger actions based on predefined rules.

## 2. Core Functionality

### Primary Actions

*   **`read_consumption`**: Triggered on a schedule (e.g., every minute), this function calls the metering system's API to get the latest reading for each meter. It stores this raw data in a time-series collection in DynamoDB.
*   **`consolidate_data`**: Runs on a schedule (e.g., hourly, daily, monthly) to process the raw readings and generate consolidated consumption data. This aggregated data is stored in a separate table for efficient querying.
*   **`check_for_anomalies`**: After each new reading, this function can apply a set of rules (e.g., consumption above a certain threshold, continuous consumption for an extended period) to detect potential issues like leaks. If an anomaly is detected, it publishes an event to notify the user or administrator.
*   **`adjust_meter_count`**: Receives a command to adjust a meter's reading, for example, after a physical meter replacement.

## 3. Data Flow

1.  **Scheduled Reading:** An AWS EventBridge (CloudWatch Events) rule triggers the agent every minute.
2.  **API Call & Storage:** The agent fetches the latest data from the external metering API and writes the raw timestamped data to a DynamoDB table optimized for time-series data.
3.  **Anomaly Detection:** The agent checks the new data against user-defined rules. If a rule is triggered (e.g., consumption > 100 liters in a minute), it publishes a "leak_detected" event to an internal SNS topic.
4.  **Consolidation:** Separate scheduled triggers (hourly, daily) invoke the agent to run consolidation jobs, calculating totals and averages and storing them in a summary table.
5.  **ERP Push:** On a monthly basis, the agent is triggered to send the consolidated monthly consumption for each unit to the `agent_erp` to be included in the condo fee bill.

## 4. Key Considerations

*   **Data Volume:** This agent will generate a high volume of data. The database schema must be designed for cost-effective storage and efficient querying of time-series data (e.g., using composite sort keys in DynamoDB).
*   **Extensibility:** Like other integration agents, it should use an adapter pattern to easily support different metering system vendors in the future.

## 5. Multi-Vendor Integration Strategy

The market for utility metering systems is fragmented, requiring a flexible integration approach.

*   **Adapter Pattern:** A generic `IMeteringAdapter` interface will define standard methods like `get_latest_readings()`. Each supported vendor will have a corresponding implementation (e.g., `ItronAdapter`, `LandisGyrAdapter`).
*   **Dynamic Adapter Loading:** The agent will determine which adapter to use based on the building's configuration, which is specified by the implementing partner.
*   **Partner Configuration:** The partner portal will feature a section for utility management where the partner can select the metering system provider for a building and input the required API access credentials.

---
status: "Defined"
category: "Agent"
last_updated: "2025-08-06"
owner: "Jomil"
dependencies:
  - "External: Superlógica API"
  - "AWS: DynamoDB (Shared Memory)"
  - "AWS: S3 (Document Storage)"
source_code: "src/agents/agent_erp/"
---

# Agent: ERP

## 1. Purpose

The ERP Agent acts as the primary bridge between BuildingOS and external Enterprise Resource Planning (ERP) systems used by property managers (e.g., Superlógica). It is responsible for synchronizing user data, handling financial queries, and ensuring that the ERP remains the single source of truth for resident and owner information.

## 2. Core Functionality

### Primary Actions

*   **`sync_users`**: Periodically fetches the list of active residents (owners and long-term tenants) from the ERP and upserts them into the BuildingOS user database. This is the core function for identity management.
*   **`get_bill`**: Retrieves a specific bill (e.g., condo fee) for a user upon request. It stores the document in S3 and returns a secure, short-lived URL.
*   **`get_consumption_data`**: Sends consolidated utility consumption data (water, gas), provided by `agent_metering`, to the ERP for billing purposes.
*   **`check_payment_status`**: Queries the ERP to check the payment status of a resident.

## 3. API Integration (Superlógica)

*   **Provider:** Superlógica
*   **Authentication:** `st_token` (API Key) provided in the request headers.
*   **Key Endpoints:**
    *   `GET /v2/financeiro/clientes`: To list and query resident data.
    *   `GET /v2/financeiro/boletos`: To retrieve billing information.
    *   APIs for posting consumption data.

## 4. Multi-Tenancy and Extensibility

The agent must be designed as a multi-tenant component from day one.
*   **Adapter Pattern:** It will use an adapter-based design, where a generic ERP interface is defined, and specific implementations (like `SuperlogicaAdapter`) are created for each supported ERP.
*   **Configuration:** API keys and endpoint URLs for each building's specific ERP will be stored securely in AWS Secrets Manager and retrieved based on the context of the request.

## 5. Data Flow

1.  **User Sync (Inbound):** A scheduled event (e.g., every hour) triggers the `sync_users` function. The agent fetches all active users from the ERP, compares them with the data in the BuildingOS DynamoDB table, and performs create, update, or disable operations as needed.
2.  **Financial Queries (On-Demand):** When a user requests a bill, the `agent_coordinator` dispatches a task to `agent_erp`. The agent calls the ERP API, retrieves the document, saves it to S3, and returns the S3 link as its task result.
3.  **Consumption Data (Outbound):** The agent is triggered by an event carrying consolidated consumption data. It then formats this data and pushes it to the appropriate endpoint in the building's ERP.

## 6. Multi-Vendor Integration Strategy

The ERP Agent is a foundational component for multi-tenancy and must be designed to support different ERP systems used by various property management companies.

*   **Adapter Pattern:** The agent's core logic will be decoupled from specific ERP implementations. It will interact with a generic `IErpAdapter` interface. For each new ERP we support (e.g., Superlógica, SCOND), a new class implementing this interface will be created (e.g., `SuperlogicaAdapter`, `ScondAdapter`).
*   **Dynamic Adapter Loading:** When a task is received, the agent will identify the building/tenant, look up their configured ERP provider in a central configuration database (DynamoDB), and dynamically load the corresponding adapter.
*   **Partner Configuration:** Our partners (e.g., property management companies) will have a dedicated section in the BuildingOS portal to configure the ERP integration for their clients. This includes selecting the provider from a list of supported ERPs and securely providing the necessary API credentials (which will be stored in AWS Secrets Manager).

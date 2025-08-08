---
status: "Defined"
category: "Agent"
last_updated: "2025-08-06"
owner: "Jomil"
dependencies:
  - "External: AirBnB API, Booking.com API"
  - "AWS: DynamoDB (Shared Memory)"
  - "Internal: agent_locks, agent_psim (via Coordinator)"
source_code: "src/agents/agent_brokers/"
---

# Agent: Brokers

## 1. Purpose

The Brokers Agent is responsible for integrating with third-party short-term rental platforms (Brokers), such as AirBnB and Booking.com. It acts as the main entry point for the entire guest hospitality journey, from receiving the reservation to initiating the check-in process.

## 2. Core Functionality

### Primary Actions

*   **`receive_reservation`**: Triggered by a webhook from a broker platform when a new booking is made. It parses the reservation data, extracts guest information, and stores it in the BuildingOS database.
*   **`receive_cancellation`**: Triggered by a webhook when a booking is cancelled. It updates the reservation status in the database and cancels any scheduled pre-check-in communications.
*   **`initiate_guest_journey`**: After storing a new reservation, this function starts the automated communication flow, typically by sending the first welcome message and the online check-in link to the guest via WhatsApp.
*   **`create_lock_code`**: As part of the check-in process, it generates a unique, time-limited access code for the smart lock of the corresponding apartment and stores it securely in DynamoDB, ready to be provisioned by the `agent_locks`.

## 3. API Integration (Brokers)

*   **Providers:** AirBnB, Booking.com, and others in the future.
*   **Mechanism:** The agent will primarily be driven by **webhooks** sent from the broker platforms. This requires exposing a secure API Gateway endpoint to receive these events.
*   **Authentication:** Each webhook request must be validated to ensure it originates from a trusted broker, typically using a signature verification mechanism provided by the platform's API.

## 4. Data Flow

1.  **Reservation Created:** A user books a property on AirBnB.
2.  **Webhook Trigger:** AirBnB sends a `reservation_created` webhook to a dedicated BuildingOS API Gateway endpoint.
3.  **Agent Invocation:** The endpoint triggers the `agent_brokers`.
4.  **Data Processing:** The agent validates the request, parses the guest and reservation data, and stores it in the `Reservations` table in DynamoDB.
5.  **Password Generation:** It generates a secure access code for the TTLock and stores it alongside the reservation data.
6.  **Journey Kick-off:** The agent initiates the communication flow, sending a welcome message and check-in link to the guest.
7.  **Provisioning Request:** The agent's successful processing can trigger subsequent tasks for the `agent_psim` and `agent_locks` (orchestrated by the `agent_coordinator`) to provision the access credentials before the guest's arrival.

## 5. Multi-Tenancy

The agent must be designed to handle reservations for thousands of different properties managed by different operators.
*   The incoming webhook URL will contain an identifier for the operator/property to route the request correctly.
*   All data stored in DynamoDB will be partitioned using the operator's or property's unique ID to ensure strict data isolation.

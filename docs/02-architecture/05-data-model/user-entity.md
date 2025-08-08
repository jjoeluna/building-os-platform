# Entity: User

## 1. Description

The `User` entity is the central model representing any individual who interacts with the BuildingOS platform. This includes long-term residents, short-term rental guests, property managers, and building staff. It serves as the primary record for identity, contact information, and status.

## 2. Attributes

| Attribute | Type | Description | Example |
|---|---|---|---|
| `userId` | String (PK) | Unique identifier for the user within BuildingOS. | `user_123abc` |
| `externalId` | String | The user's ID in an external system (e.g., ERP or Broker). | `superlogica_456` |
| `source` | String | The system from which the user was originally sourced. | `superlogica`, `airbnb` |
| `buildingId` | String | The ID of the building the user is associated with. | `bldg_789xyz` |
| `unitId` | String | The ID of the specific unit (apartment) the user is linked to. | `unit_101` |
| `name` | String | The user's full name. | `John Doe` |
| `email` | String | The user's email address. | `john.doe@email.com` |
| `phone` | String | The user's phone number. | `+5511999998888` |
| `userType` | String | The user's role or profile. | `resident`, `guest`, `staff` |
| `status` | String | The current status of the user's account. | `active`, `inactive` |
| `accessStartDate` | ISO 8601 | The timestamp when the user's access becomes valid. | `2025-12-25T14:00:00Z` |
| `accessEndDate` | ISO 8601 | The timestamp when the user's access expires (crucial for guests). | `2025-12-28T11:00:00Z` |
| `facialProfileId` | String | The ID of the user's profile in the external PSIM system. | `psim_face_001` |
| `createdAt` | ISO 8601 | The timestamp of the record's creation. | `2025-08-06T10:00:00Z` |
| `updatedAt` | ISO 8601 | The timestamp of the last update to the record. | `2025-08-06T10:00:00Z` |

## 3. Relationships

*   **Belongs to one `Building`:** Each user is associated with a single building.
*   **Can be associated with one `Unit`:** A user is typically linked to one apartment or unit.
*   **Can have multiple `AccessLogs`:** Tracks all access events for the user.
*   **Can have multiple `Reservations`:** If the user is a guest.
*   **Can have multiple `MaintenanceTickets`:** Tracks all maintenance requests opened by the user.

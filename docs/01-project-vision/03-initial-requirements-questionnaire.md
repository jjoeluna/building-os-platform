# Initial Requirements Questionnaire: BuildingOS Project

## Part 1: Vision and Business (For Project Charter)

The objective of this section is to understand the "why" of the project, aligning business vision with technical objectives.

### 1. General Vision and Problem

- What is the main problem this project aims to solve?

This project aims to create a system capable of integrating all condominium functionalities with an artificial intelligence system that helps everyone involved in their daily tasks.

- Could you describe the current scenario that motivates the creation of BuildingOS?  
<br/>- Who faces this problem today? (Ex: residents, condominium administrators, maintenance team?)  
<br/>- What is the long-term vision for this product? Where do you see it in 3 or 5 years?

### 2. Business Objectives  
<br/>- What are the 3 main business objectives you expect to achieve with this project? (Ex: reduce operational costs, create a new revenue stream, improve customer satisfaction, etc.)  
<br/>- How will we measure the success of these objectives? What numbers (KPIs) will tell us we were successful? (Ex: "reduce maintenance call response time by 50%", "increase rental renewal rate by 10%").

### 3. Project Scope  
<br/>- For the first version (MVP), what are the absolutely essential functionalities the system needs to have?  
**Answer:** To ensure a focused launch that validates the most critical integrations, the scope will be divided into two clear phases:

**Phase 1: The MVP (Foundation of Trust and Access)** The MVP will focus on solving the central problem of **identity and access**, which is the foundation for all other operations in a mixed-use environment.

* **1. Conversational Chat Interface:** The virtual assistant (via web) as the central point of interaction.
* **2. User Synchronization Agent (ERP):**
  * **Core Integration:** Connect with the **Superlógica** ERP as the source of truth for owners and annual tenants.
  * **Functionality:** Automatically synchronize the user base (active residents) from the ERP to BuildingOS, ensuring only authorized people have access.
* **3. Access Control Agent (PSIM):**
  * **Core Integration:** Connect with the **Situator** PSIM.
  * **Functionality:** Provision synchronized users from the ERP into the PSIM, creating or updating their profiles to ensure basic physical access.
* **4. Elevator Agent (Neomot API):**
  * **Functionality:** Allow an authenticated user, via chat, to **call the elevator** to their floor and receive **arrival notification**.

**Phase 2: The Final Version Vision (The Hospitality and Operations Ecosystem)** The final version expands the MVP to become a complete operations and hospitality management platform, satisfying all stakeholders.

* **Module 1: Hospitality and Short-term Rental Management (Brokers):**
  * Integration with **AirBnB and Booking.com** to automatically receive reservations.
  * Automation of guest communication flow via WhatsApp (instructions, check-in reminders).
  * **Online check-in** process with document capture and photo.
  * **Automatic and temporary** provisioning of access credentials (facial in PSIM, passwords for **TTLock** locks).
  * Portal for the owner/operator to view reservations and interactions.
* **Module 2: Proactive and Intelligent Operations:**
  * Receive real-time access events from **PSIM**.
  * **Proactive Automation:** When detecting the entry of an authorized resident or guest into the building (via facial or vehicle tag), the system **automatically calls the elevator** to the access floor (ground/garage) and notifies the user.
  * **Intelligent Maintenance:** The system will differentiate calls: a problem within a short-term rental apartment generates a task for the **operator**, while a problem in a common area triggers the building's **maintenance team**.
  * **Consumption Measurement and Alerts:** Integrate with water/gas meters to send data to the ERP, allow queries via chat, and **alert about abnormal consumption**.
* **Module 3: Security and Compliance for Mixed Use:**
  * **Visibility for Front Desk/Security:** The building team will have a clear view in their system of who the guests are, which unit they are in, and the period of their stay.
  * **Dynamic Access Profiles:** The system will manage different profiles in PSIM (Resident, Guest, Service Provider), with distinct permissions and validities.
* **Module 4: Enhanced Resident Experience:**
  * **Fair Resource Management:** The common area reservation system will have rules to ensure that use by guests does not prejudice resident access.
  * **Directed Communication:** BuildingOS will ensure that guest requests are always directed to their operators, avoiding overloading the condominium administration.
* **Module 5: Partner Platform and Ecosystem:**
  * Develop an "adapter" architecture to easily integrate with other market ERPs.
  * Create a portal for partner companies (security, maintenance, etc.) to sell and manage BuildingOS for their own clients.

- Is there anything that, for now, is explicitly out of scope? (Ex: "In this phase, we won't integrate with security camera systems", "There won't be an iOS app, only Android and Web").
<br/>**Answer:** Yes, to maintain **MVP** focus, the following items are explicitly **out of initial scope**:

* All of **Phase 2 (Final Version Vision)**, including broker integration (AirBnB, Booking), proactive elevator automation, and consumption measurement.
* Native applications (iOS/Android). Focus will be on a responsive Web interface.
* Integration with camera systems (CCTV).
* Common area reservation module.
* Financial integrations (beyond user synchronization).
* Correspondence management module.

### 4. Stakeholders (Interested Parties)

<br/>- Who are the key people involved in this project?
<br/>- Who is the Primary Contact for product decisions (Product Owner)?
<br/>- Who is the Primary Contact for technical decisions (Tech Lead)?
<br/>**Answer:**
*   **Core Team (Blubrain.ai):**
    *   **Jomil:** Founder, responsible for product vision (Product Owner) and technical architecture (Tech Lead).
    *   **Licca:** Inspiration for the AI assistant persona, serving as a guide for user experience.
*   **Stakeholder Groups (Users and Clients):**
    *   **End Users:** Residents, Tenants (annual and temporary), Syndics, Administrators, Janitors, Doormen, etc. Their needs and feedback are the main input for product development.
    *   **Clients and Partners:** Construction companies, Condominium Management Companies and Partner Companies that will market the solution. Their business objectives drive the product's market strategy.
*   **Primary Contact for Product Decisions (Product Owner):**
    *   **Jomil.**
*   **Primary Contact for Technical Decisions (Tech Lead):**
    *   **Jomil.**

## Part 2: Functional and Non-Functional Requirements (For Requirements)

The objective of this section is to detail the "what" and "how" of the system.

### 5. Functionalities (User Stories)

Below is a comprehensive list of User Stories that describe the needs of the different users in the BuildingOS ecosystem:

#### 5.1. For the Resident / Annual Tenant
1.  **As a resident, I want** the garage gate to open automatically (via LPR or tag) when my car approaches **so that** I can have quick and seamless access.
2.  **As a resident, I want to** call the elevator to my floor while leaving the apartment **so that** it is waiting for me when I get to the hallway.
3.  **As a resident, I want to** be notified when a delivery arrives and the courier leaves it in a Smart Locker **so that** I can retrieve it with a unique code securely and conveniently.
4.  **As a resident, I want to** pre-authorize a visitor for the weekend **so that** they can enter using facial recognition without bothering me.
5.  **As a resident, I want to** be notified when a package for me arrives at the front desk **so that** I can pick it up.
6.  **As a resident, I want to** create a recurring access permission for my cleaner (every Friday, 8am-12pm) **so that** I don't have to manually grant access every week.
7.  **As a resident, I want to** see the elevator's status (current floor and direction) **so that** I can decide whether to wait or take the stairs.
8.  **As a resident, I want to** check the availability of and book the barbecue area via chat **so that** I can plan my event quickly.
9.  **As a resident, I want to** be placed on a waiting list for the tennis court **so that** I get notified if a slot becomes available.
10. **As a resident, I want to** pay the reservation fee for the party hall via Pix through the system **so that** the process is 100% digital.
11. **As a resident, I want to** look up the rules for using the gym **so that** I know the peak hours and regulations.
12. **As a resident, I want to** receive a reminder for my common area booking one day in advance **so that** I don't forget.
13. **As a resident, I want to** report a leak in my garage ceiling by sending a photo **so that** maintenance is dispatched with the exact location.
14. **As a resident, I want to** track the status of my maintenance request **so that** I know when the issue will be resolved.
15. **As a resident, I want to** rate the maintenance service after completion **so that** I can provide feedback on the quality.
16. **As a resident, I want to** access a history of all my requests **so that** I have a record of what has been asked.
17. **As a resident, I want to** be notified when the maintenance technician is on their way to my apartment **so that** I can be ready to receive them.
18. **As a resident, I want to** receive important announcements from the manager (like a water outage) on my phone **so that** I am always informed.
19. **As a resident, I want to** participate in a poll about the new facade color for the building **so that** my opinion is considered.
20. **As a resident, I want to** ask "where is my apartment's water meter?" **so that** I get the exact location.
21. **As a resident, I want to** access the minutes of the last condominium meeting **so that** I can stay updated on decisions.
22. **As a resident, I want to** access a community classifieds section **so that** I can sell a bicycle to a neighbor.
23. **As a resident, I want to** be notified about social events in the condominium, like the summer party **so that** I can participate.
24. **As a resident, I want to** request a duplicate of my condo fee bill **so that** I can make the payment.
25. **As a resident, I want to** check my water and gas consumption for the last month **so that** I can understand my bill.
26. **As a resident, I want to** register my new vehicle in the system **so that** its access to the garage is enabled.
27. **As a resident, I want to** receive an alert for abnormal water consumption **so that** I can check for a possible leak.
28. **As a resident, I want to** trigger a silent panic button via chat **so that** the security team is discreetly notified in an emergency.
29. **As a resident, I want to** be notified if the fire alarm on my floor is activated **so that** I can evacuate safely.
30. **As a resident, I want to** view the access history for my apartment (if there's a smart lock) **so that** I know who entered and when.

#### 5.2. For the Short-Term Rental Guest
1.  **As a guest, I want to** receive a link for online check-in via WhatsApp as soon as my reservation is confirmed **so that** I can speed up the process.
2.  **As a guest, I want to** securely submit a photo of my ID through the check-in link **so that** I comply with registration requirements.
3.  **As a guest, I want to** receive automatic reminders to check-in **so that** I don't forget to complete the process before my trip.
4.  **As a guest, I want to** receive clear instructions on how to get to the building, including the address and entry rules **so that** my arrival is smooth.
5.  **As a guest, I want to** automatically receive the password for the apartment lock and the Wi-Fi on my check-in day **so that** I have full autonomy.
6.  **As a guest, I want** my face to be my access credential for permitted common areas **so that** I don't need to carry keys or cards.
7.  **As a guest, I want to** be welcomed by the elevator waiting for me on the ground floor upon my first entry **so that** I have a "wow" welcome experience.
8.  **As a guest, I want to** ask the assistant "what is the voltage of the outlets?" **so that** I can get useful information about the apartment.
9.  **As a guest, I want to** request clean towels or other hospitality items via chat **so that** my host is notified.
10. **As a guest, I want to** report that the air conditioning is not working **so that** the property operator can arrange for a repair.
11. **As a guest, I want to** receive suggestions for restaurants and attractions near the building **so that** I can better enjoy my stay.
12. **As a guest, I want** my questions about the apartment to be answered by the assistant **so that** I don't have to contact the host for simple things.
13. **As a guest, I want** my maintenance requests to be automatically routed to my host **so that** the right person solves my problem.
14. **As a guest, I want to** have a direct and recorded communication channel with the host **so that** I have security about what was agreed upon.
15. **As a guest, I want to** receive check-out instructions on the morning of my departure **so that** I know exactly what to do.
16. **As a guest, I want to** request a late check-out via chat **so that** the host can easily approve or deny it.
17. **As a guest, I want to** inform that I have left the apartment **so that** the cleaning team can be dispatched.
18. **As a guest, I want to** be able to rate my stay directly via chat **so that** I can provide my feedback simply.
19. **As a guest, I want to** receive a discount coupon for a future stay **so that** I am encouraged to return.
20. **As a guest, I want to** be sure that my data and access credentials will be automatically revoked after check-out **so that** I feel secure.

#### 5.3. For the Property Owner / Rental Operator
1.  **As an operator, I want** my AirBnB and Booking.com reservations to be automatically imported into my dashboard **so that** I have a centralized view.
2.  **As an operator, I want to** define automated message templates (welcome, check-in, check-out) **so that** communication with guests is standardized and efficient.
3.  **As an operator, I want to** see all guests with pending check-ins **so that** I can track who still needs to submit their documents.
4.  **As an operator, I want to** manually approve a check-in after reviewing the documents **so that** access is granted securely.
5.  **As an operator, I want to** be notified in real-time when my guest physically checks in (first entry) **so that** I know they have arrived safely.
6.  **As an operator, I want to** have a "super chat" where I can view and respond to all my guests' conversations with the assistant **so that** I can intervene when necessary.
7.  **As an operator, I want to** be able to extend a guest's stay in the system **so that** their access credentials are automatically updated.
8.  **As an operator, I want to** be the first to be notified about a maintenance issue in my apartment **so that** I can dispatch my trusted team.
9.  **As an operator, I want to** create a work order for my cleaning team as soon as a guest checks out **so that** the apartment is prepared for the next one.
10. **As an operator, I want to** authorize access for an air conditioning technician for a specific date and time **so that** they can perform the repair without my presence.
11. **As an operator, I want to** have a maintenance history for each of my properties **so that** I can control costs and repair history.
12. **As an operator, I want to** view a calendar with the occupancy of all my properties **so that** I can manage my availability.
13. **As an operator, I want to** receive a weekly financial summary with the revenue from my rentals **so that** I can track my income.
14. **As an operator, I want** the system to alert me about excessive water or energy consumption in an apartment **so that** I can investigate a potential issue.
15. **As an operator, I want to** have a log of all accesses to my apartment (via smart lock) **so that** I have a security record.
16. **As an operator, I want to** be able to revoke a guest's access immediately in case of problems **so that** I can ensure the security of my property.
17. **As an operator, I want** access credentials (facial, passwords) to expire automatically at the check-out time **so that** I don't have to worry about removing them manually.
18. **As an operator, I want to** register my team members (cleaning, maintenance) in the system **so that** I can assign tasks to them.
19. **As an operator, I want to** receive consolidated guest reviews and feedback **so that** I can improve my service.
20. **As an operator, I want to** access the system through a simple and intuitive web portal **so that** I can manage my properties from anywhere.

#### 5.4. For the Building Administrator / Manager
1.  **As a manager, I want to** send segmented announcements (by tower, floor, or only to owners) **so that** the information is relevant to the recipients.
2.  **As an administrator, I want to** have a dashboard with the main building KPIs (open tickets, delinquency rates, common area usage) **so that** I have a general overview of operational health.
3.  **As a manager, I want to** create and send polls to residents about important decisions **so that** the voting process is more agile and documented.
4.  **As an administrator, I want to** have a central repository for documents (meeting minutes, bylaws, financial statements) **so that** residents can consult them autonomously.
5.  **As a manager, I want to** be notified about security incidents (panic button pressed, fire alarm) in real-time **so that** I can take necessary action.
6.  **As an administrator, I want to** view all maintenance tickets on a single panel, with status and priority **so that** I can manage the team's work.
7.  **As an administrator, I want to** assign a maintenance ticket to a specific team member **so that** responsibility is clear.
8.  **As a manager, I want to** approve repair budgets directly through the system **so that** the process is faster and traceable.
9.  **As an administrator, I want to** generate reports on the most common types of maintenance issues **so that** we can identify areas needing investment.
10. **As an administrator, I want to** be alerted when a high-priority ticket is not addressed within the SLA **so that** I can intervene.
11. **As an administrator, I want to** have a complete log of all service provider accesses **so that** I have a security audit trail.
12. **As a manager, I want to** have a clear view of which apartments are being used for short-term rentals and who the guests are **so that** building security is maintained.
13. **As an administrator, I want to** register a new recurring service provider (e.g., gardening) and define their access permissions **so that** they have controlled autonomy.
14. **As an administrator, I want to** revoke an ex-employee's access from all areas of the building with a single command **so that** security is guaranteed.
15. **As a manager, I want** individual water and gas consumption data to be sent automatically to the property management ERP **so that** billing is accurate and without manual effort.

### 6. Non-Functional Requirements (The "Qualities" of the System)

- Performance: Is there any operation that is critical in terms of time? (Ex: "The opening of a door must occur in less than 2 seconds").
<br/>**Answer:** Yes, performance is a fundamental pillar for the system's confidence and usability. Requirements are defined by operation domains and measured in the 95th percentile (p95).

*   **Physical Access Domain (Ultra-Low Latency):**
    *   **SLO:** System response in **< 1.5 seconds**.
    *   **Operations:** Garage gate opening (via LPR/Tag), pedestrian doors (via facial), gates and common area doors.
    *   **Justification:** Latency must be imperceptible to the user, equivalent or better than a traditional remote control.

*   **User Interaction Domain (Low Latency):**
    *   **SLO:** Assistant response in **< 3 seconds**.
    *   **Operations:** Elevator call via chat, factual question responses.
    *   **Justification:** Conversational interaction needs to be agile to maintain engagement.

*   **Portal Operations Domain (Moderate Latency):**
    *   **SLO:** Page loading and dashboards in **< 5 seconds**.
    *   **Operations:** Opening the reservations panel, viewing maintenance tickets.
    *   **Justification:** Operators and administrators need fluidity to perform their management tasks.

*   **Asynchronous Processing Domain (Non-critical in real-time):**
    *   **SLO:** Complete processing in **< 2 minutes**.
    *   **Operations:** Synchronization of a new AirBnB reservation, provisioning of a new user in PSIM.
    *   **Justification:** Background operations that need to be completed within a reasonable time.

- Scalability: What is the expected number of users (or apartments) for the launch? And what is the growth projection for the first year?
<br/>**Answer:** Scalability strategy is divided into two phases:

**Phase 1: Launch (MVP)**
*   **Scope:** 1 to 5 buildings (~100-500 units, ~300-1500 users).
*   **Concurrency:** Support **50 concurrent access operations** per minute and **200 simultaneous chat users**.
*   **Architecture:** Serverless-first (Lambda, DynamoDB, SNS) architecture should scale automatically for this load.

**Phase 2: Final Vision (Long Term)**
*   **Scope:** 300 buildings (~45,000 units, ~135,000 users).
*   **Peak Concurrency:**
    *   **Physical Access:** Support **10,000 concurrent access operations** per minute.
    *   **Chat Interactions:** Support **15,000 simultaneous users**.
    *   **Event Processing:** Ingest and process up to **1,000 events per second** from integrations.
*   **Architecture Strategy:**
    *   **Multi-Tenancy:** Native multi-tenant architecture with logical data isolation.
    *   **Regional Scalability:** Infrastructure as code (Terraform) for easy replication across multiple AWS regions.
    *   **Queues and Resilience:** Mass use of SNS/SQS to absorb peak loads and ensure message durability.

- Availability: Does the system need to run 24/7? What is the tolerance for occasional failures or downtime? (Ex: "Is it acceptable to have a planned maintenance window of 1 hour per month?").
<br/>**Answer:** Yes, availability is a critical requirement, especially for access and security functionalities. The availability strategy will be based on clear Service Level Objectives (SLOs):

*   **Uptime SLO:** **99.9%** monthly availability.
    *   **This translates to:** No more than **43.8 minutes** of unplanned downtime per month.
    *   **Justification:** Ensures that the system is operational most of the time, which is essential for a service that controls physical access.

*   **High Availability Strategy:**
    *   **Multi-AZ Infrastructure:** All architecture components (Lambdas, DynamoDB, API Gateway, SNS/SQS) will be deployed across multiple Availability Zones (AZs) of the AWS for guaranteed service uptime in case of a single data center failure.
    *   **Resilient Database:** Amazon DynamoDB offers synchronous data replication across multiple AZs by default.
    *   **Stateless Computing:** Our agents (Lambdas) are stateless, meaning if one instance fails, another can assume the work instantly.

*   **Maintenance Policy:**
    *   **Zero Downtime Deployments:** Software updates will be performed using strategies like Blue/Green or Canary, which allow the system to be updated without taking it offline.
    *   **Maintenance Windows:** Planned maintenance that requires downtime (e.g., database migrations) will be scheduled during low-usage periods (e.g., between 3am and 4am) and communicated in advance.

- Security: - What are the most sensitive data the system will store? (Ex: personal data of residents, access logs).
<br/>**Answer:** Security is an inalienable pillar of BuildingOS. The security strategy covers data protection, compliance, and infrastructure security.

*   **Sensitive Data Stored:**
    *   **Personally Identifiable Information (PII):** Full name, CPF, RG, email, resident phone numbers, guests, and service providers.
    *   **Biometric Data:** Photos for facial recognition system.
    *   **Access Logs:** Detailed logs of who accessed which area and when.
    *   **Financial Information:** Condominium fee payment status (via ERP integration).
    *   **Private Communications:** Chat history.

- Are there any compliance requirements, such as LGPD (General Data Protection Law)?
<br/>**Answer:** Yes, **LGPD compliance is a mandatory requirement**. The system will be developed from the start following **Privacy by Design** principles to ensure total compliance.
*   **Consent:** Users will have to explicitly consent to the use of their data through clear terms of service.
*   **Transparency and Access:** Users can request a report of all data the system stores about them.
*   **Right to Be Forgotten:** There will be a process for the anonymization or complete deletion of a user's data when they leave the condominium or request it.
*   **Application and Infrastructure Security Strategy:**
    *   **Encryption in Transit and at Rest:** All data will be encrypted. Communication between services and with the end user will use TLS 1.2+. Data in databases (DynamoDB) and other storages (S3) will be encrypted at rest using AWS KMS.
    *   **Principle of Least Privilege:** Each component of the architecture (each Lambda) will have only the strictly necessary permissions to perform its function.
    *   **Robust Authentication and Authorization:** Access to APIs will be protected, and user identity will be validated in all requests.
    *   **Auditing and Logs:** All critical actions (especially access and data modification) will be logged for auditability.
    *   **Credential Security:** All passwords and API keys of third-party services will be securely stored in AWS Secrets Manager, not in the source code.

- Usability: How familiar are the end users (residents and administrators) with technology? Does the system need to be extremely simple and intuitive?
<br/>**Answer:** Yes, usability is a critical pillar to ensure BuildingOS's adoption and success, given the extremely diverse target audience.

*   **Target Audience:** The system will be used by a wide spectrum of users, from foreign guests and young residents (highly tech-savvy) to elderly residents, doormen, and maintenance teams (potentially with low tech familiarity).

*   **Design Principle: "Conversation First" (Conversation-First):**
    *   The main interface will be the **chat**, as conversational language is the most intuitive way for human interaction, minimizing the learning curve.
    *   The assistant must be able to understand varied intents, including typos and common slang.

*   **Guidelines for Usability by Interface:**
    *   **Conversational Interface (Chat):** It should be as simple as using WhatsApp, with proactive suggestions for functionalities and total accessibility (WCAG 2.1 AA).
    *   **Operator Portal (Web):** It should be focused on efficiency, with task-oriented design, visual dashboards, and total responsiveness for mobile use.
    *   **Building Team Panel (Front Desk/Maintenance):** It should prioritize radical simplicity, with large buttons, clear text, visual/auditory alerts, and low cognitive load, optimized for tablets or kiosks.

*   **General Guidelines:**
    *   **Support for Multiple Languages:** Starting with Portuguese and English.
    *   **Onboarding and Help:** Interactive tutorials for the first portal use and an easily accessible "Help" section on all screens.

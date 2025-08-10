# 📖 BuildingOS Documentation Tree

**Complete documentation structure from the project root**

---

## 🏗️ **Project Structure Overview**

Based on the root `README.md`, here's the complete project structure:

```
🏢 building-os-platform/
├── 📄 README.md                                    # 🏢 Main project overview and quick start
├── 📖 docs/                                        # 📖 Complete project documentation
│   ├── 📄 README.md                               # 📖 Main documentation index
│   ├── 📊 00-business-context/                    # Business context and campaign brief
│   │   ├── 📄 README.md                          # Business context overview
│   │   └── 📄 LIT760-Campaign-Brief.md          # Original campaign brief
│   ├── 📋 01-project-vision/                     # Project vision and requirements
│   │   ├── 📄 README.md                          # Project vision overview
│   │   ├── 📄 01-charter.md                      # Project charter and vision
│   │   ├── 📄 02-requirements.md                 # Functional and non-functional requirements
│   │   └── 📄 03-initial-requirements-questionnaire.md # Detailed requirements questionnaire
│   ├── 🏗️ 02-architecture/                      # System architecture and design
│   │   ├── 📄 README.md                          # Architecture overview
│   │   ├── 🏗️ 01-solution-architecture/         # Solution architecture
│   │   │   └── 📄 solution-architecture.md      # Technical blueprint and C4 diagrams
│   │   ├── 📋 02-adr/                           # Architecture Decision Records
│   │   ├── 🗄️ 03-data-model/                    # Database schemas and data relationships
│   │   ├── 🔧 04-components/                    # Software components registry
│   │   ├── 🔌 05-api-contract/                  # API specifications
│   │   ├── 📡 06-sns/                           # Event-driven communication patterns
│   │   ├── 🤖 98-ai-prompts/                    # AI assistant contexts
│   │   │   ├── 📄 README.md                     # Architecture AI prompts overview
│   │   │   └── 📄 architect-context-prompt.md   # Architecture context prompt
│   │   └── 📚 99-lessons/                       # Architecture lessons learned
│   ├── 🛠️ 03-development/                       # Development tools and status
│   │   ├── 📄 README.md                          # Development overview
│   │   ├── 📊 01-project-management/            # Current development status
│   │   │   ├── 📄 README.md                     # Development status overview
│   │   │   ├── 📄 current-sprint.md             # Current sprint status
│   │   │   ├── 📄 metrics.md                    # Development metrics
│   │   │   ├── 📄 completed.md                  # Completed features
│   │   │   └── 📄 backlog.md                    # Development backlog
│   │   ├── 🔧 02-cli-commands-reference/        # CLI commands and procedures
│   │   ├── ⚙️ 03-setup-guide/                   # Development environment setup
│   │   ├── 🚀 05-deployment-guide/              # Deployment procedures
│   │   ├── 🔍 06-troubleshooting-guide/         # Troubleshooting guides
│   │   ├── 🤖 98-ai-prompts/                    # AI development prompts
│   │   │   ├── 📄 README.md                     # Development AI prompts overview
│   │   │   └── 📄 developer-context-prompt.md   # Development context prompt
│   │   └── 📚 99-lessons/                       # Development lessons learned
│   └── ⚙️ 04-operations/                         # Production operations and monitoring
│       ├── 📄 README.md                          # Operations overview
│       ├── 📊 01-monitoring-strategy/           # Monitoring and alerting system
│       │   ├── 📄 README.md                     # Monitoring strategy overview
│       │   ├── 📄 monitoring-strategy.md        # Core monitoring philosophy
│       │   ├── 📄 monitoring-process.md         # Detailed monitoring workflows
│       │   └── 📄 monitoring-summary.md         # Executive summary
│       ├── 📋 02-runbook-template/              # Operational runbooks
│       ├── 🔍 03-post-mortem-template/          # Incident analysis templates
│       ├── 🤖 98-ai-prompts/                    # AI operations prompts
│       │   ├── 📄 README.md                     # Operations AI prompts overview
│       │   └── 📄 operations-context-prompt.md  # Operations context prompt
│       ├── 📚 99-lessons/                       # Operations lessons learned
│       ├── 📄 terraform-best-practices-checklist.md # Terraform best practices
│       ├── 📄 session-summary-2025-01-08.md    # Session summary
│       ├── 📄 terraform-refactoring-guide.md   # Terraform refactoring guide
│       ├── 📄 terraform-migration-summary.md   # Terraform migration summary
│       └── 📄 terraform-testing-results.md     # Terraform testing results
├── 🏗️ terraform/                                 # Infrastructure as Code
│   ├── 📄 versions.tf                           # Terraform version constraints
│   ├── 🏗️ modules/                             # Reusable Terraform modules
│   └── 🌍 environments/                         # Environment-specific configurations
│       ├── 🚀 dev/                             # Development environment
│       ├── 🧪 stg/                             # Staging environment
│       └── 🏭 prd/                             # Production environment
├── 🤖 src/                                      # Application source code
│   ├── 🤖 agents/                              # Lambda agent implementations
│   ├── 🔧 tools/                               # Utility tools and scripts
│   ├── 🎭 personas/                            # User persona implementations
│   ├── 🔄 triggers/                            # Event triggers and handlers
│   └── 📚 layers/                              # Lambda layers (shared code)
├── 🧪 tests/                                   # Test suites and test data
│   ├── 🧪 agents/                              # Agent-specific tests
│   ├── 🧪 api/                                 # API integration tests
│   └── 🧪 tools/                               # Tool-specific tests
├── 🎨 frontend/                                # User interface components
├── 📊 monitoring/                              # Monitoring and observability
├── 📋 scripts/                                 # Automation and deployment scripts
├── 📄 LICENSE                                  # MIT License
└── 📄 .gitignore                               # Git ignore rules
```

---

## 🤖 **AI Prompts Documentation Structure Awareness**

**MANDATORY:** All AI assistants working on the BuildingOS platform MUST follow these documentation navigation guidelines:

### **🚨 Critical Documentation Structure Awareness**

Before starting any work, AI assistants MUST:

1. **Find the Main Documentation Index:** Always start by reading `docs/README.md` - this is the **main documentation index** that contains the complete project structure and navigation guide.

2. **Understand Documentation Tree:** Review `docs/documentation-tree.md` for the complete project structure overview and quick navigation paths.

3. **Locate Relevant Documents:** Use the documentation structure to find the specific documents you need for your task.

### **Documentation Navigation Strategy by Role:**

#### **🛠️ For Development Work:**
- **Start Here:** `docs/README.md` - Main documentation index
- **Structure Overview:** `docs/documentation-tree.md` - Complete project structure
- **Development Focus:** `docs/03-development/README.md` - Development-specific documentation
- **Current Sprint:** `docs/03-development/01-project-management/current-sprint.md` - Active sprint status
- **Architecture Reference:** `docs/02-architecture/README.md` - System architecture
- **Operations Reference:** `docs/04-operations/README.md` - Operations and monitoring

#### **🏗️ For Architecture Work:**
- **Start Here:** `docs/README.md` - Main documentation index
- **Structure Overview:** `docs/documentation-tree.md` - Complete project structure
- **Architecture Focus:** `docs/02-architecture/README.md` - Architecture-specific documentation
- **Solution Architecture:** `docs/02-architecture/01-solution-architecture/solution-architecture.md` - Technical blueprint and C4 diagrams
- **Development Reference:** `docs/03-development/README.md` - Development status and current sprint
- **Operations Reference:** `docs/04-operations/README.md` - Operations and monitoring

#### **⚙️ For Operations Work:**
- **Start Here:** `docs/README.md` - Main documentation index
- **Structure Overview:** `docs/documentation-tree.md` - Complete project structure
- **Operations Focus:** `docs/04-operations/README.md` - Operations-specific documentation
- **Monitoring Strategy:** `docs/04-operations/01-monitoring-strategy/README.md` - Monitoring and alerting system
- **Development Reference:** `docs/03-development/README.md` - Development status and current sprint
- **Architecture Reference:** `docs/02-architecture/README.md` - System architecture

### **Quick Documentation Paths:**

#### **For New Features:**
`docs/03-development/01-project-management/current-sprint.md` → `docs/02-architecture/01-solution-architecture/solution-architecture.md`

#### **For API Changes:**
`docs/02-architecture/05-api-contract/api-contract.md` → `docs/03-development/02-cli-commands-reference/cli-commands-reference.md`

#### **For Infrastructure Issues:**
`docs/04-operations/terraform-best-practices-checklist.md` → `docs/03-development/05-deployment-guide/README.md`

#### **For Monitoring Issues:**
`docs/04-operations/01-monitoring-strategy/README.md` → `docs/04-operations/02-runbook-template/runbook-template.md`

#### **For System Design:**
`docs/02-architecture/01-solution-architecture/solution-architecture.md` → `docs/02-architecture/04-components/README.md`

#### **For Incident Response:**
`docs/04-operations/03-post-mortem-template/post-mortem-template.md` → `docs/04-operations/99-lessons/README.md`

---

## 🎯 **Key Documentation Categories**

### **📊 Business Context (00-business-context/)**
- **Purpose**: Business context and campaign brief
- **Key Documents**: LIT760 Campaign Brief
- **Audience**: Stakeholders, business teams

### **📋 Project Vision (01-project-vision/)**
- **Purpose**: Business goals and requirements
- **Key Documents**: Charter, Requirements, Questionnaire
- **Audience**: Product owners, business analysts

### **🏗️ Architecture (02-architecture/)**
- **Purpose**: System design and decisions
- **Key Documents**: Solution Architecture, API Contract, ADRs
- **Audience**: Architects, developers, technical leads

### **🛠️ Development (03-development/)**
- **Purpose**: Implementation tools and status
- **Key Documents**: Development Status, CLI Commands, Setup Guide
- **Audience**: Developers, DevOps engineers

### **⚙️ Operations (04-operations/)**
- **Purpose**: Production maintenance and monitoring
- **Key Documents**: Monitoring Strategy, Runbooks, Post-Mortems
- **Audience**: Operations teams, SRE engineers

---

## 🚀 **Quick Navigation Paths**

### **For New Team Members**
1. **📋 Project Charter** → `docs/01-project-vision/01-charter.md`
2. **🏗️ Solution Architecture** → `docs/02-architecture/01-solution-architecture/solution-architecture.md`
3. **🛠️ Development Status** → `docs/03-development/01-project-management/README.md`
4. **⚙️ Setup Guide** → `docs/03-development/03-setup-guide/setup-guide.md`

### **For Development Work**
1. **📊 Current Status** → `docs/03-development/01-project-management/current-sprint.md`
2. **🔧 CLI Commands** → `docs/03-development/02-cli-commands-reference/cli-commands-reference.md`
3. **🔌 API Reference** → `docs/02-architecture/05-api-contract/api-contract.md`
4. **🤖 AI Context** → `docs/03-development/98-ai-prompts/README.md`

### **For Architecture Work**
1. **🏗️ System Design** → `docs/02-architecture/01-solution-architecture/solution-architecture.md`
2. **📋 Decisions** → `docs/02-architecture/02-adr/`
3. **🔌 API Contract** → `docs/02-architecture/05-api-contract/api-contract.md`
4. **📡 Event System** → `docs/02-architecture/06-sns/`

### **For Operations Work**
1. **📊 Monitoring** → `docs/04-operations/01-monitoring-strategy/README.md`
2. **📋 Runbooks** → `docs/04-operations/02-runbook-template/runbook-template.md`
3. **🔍 Post-Mortems** → `docs/04-operations/03-post-mortem-template/post-mortem-template.md`
4. **🤖 AI Context** → `docs/04-operations/98-ai-prompts/README.md`

---

## 📈 **Project Status**

### **Development Progress**
- ✅ **Fase 1: Fundamentals** - 100% Complete (8/8 items)
- 🔄 **Fase 2: Structural** - 83% Complete (5/6 items)
- ⏳ **Fase 3: Advanced** - 0% Complete (0/6 items)
- 🔄 **Fase 4: Compliance** - 75% Complete (3/4 items)
- ⏳ **Fase 5: Multi-Environment** - 0% Complete (0/3 items)

### **Key Achievements**
- ✅ **10 Lambda functions** migrated to modular architecture
- ✅ **Event-driven architecture** implemented with SNS topics
- ✅ **Infrastructure as Code** with Terraform modules
- ✅ **Observability** with CloudWatch and X-Ray
- ✅ **Multi-environment** support (dev/stg/prd)

---

## 🏗️ **Architecture Overview**

### **Core Components**
- **🤖 Agent Persona** - User interface and intention processing
- **🧠 Agent Director** - Strategic planning and mission creation
- **⚙️ Agent Coordinator** - Tactical execution and task orchestration
- **🛗 Agent Elevator** - Elevator control and monitoring
- **🚪 Agent PSIM** - Physical security integration
- **💼 Agent ERP** - Financial and resident data management

### **Technology Stack**
- **Cloud Platform:** AWS (Lambda, SNS, DynamoDB, API Gateway, CloudWatch)
- **Infrastructure:** Terraform (Infrastructure as Code)
- **Runtime:** Python 3.11 (Lambda functions)
- **Communication:** SNS topics (event-driven architecture)
- **Storage:** DynamoDB (state management), S3 (file storage)
- **Monitoring:** CloudWatch (logs, metrics, alarms)

---

## 🎯 **Documentation Principles**

- **Single Source of Truth** - Each topic has one authoritative document
- **Living Documentation** - Updated continuously with implementation
- **User-Centric** - Organized by user needs and workflows
- **Version Controlled** - All documentation in Git
- **AI-Ready** - Structured for AI assistance and automation

---

## 📚 **Essential Documentation Links**

### **From Root README**
- **[📖 Complete Documentation](docs/README.md)** - Full project documentation
- **[🏗️ Architecture](docs/02-architecture/README.md)** - System design and architecture
- **[🛠️ Development Status](docs/03-development/01-project-management/README.md)** - Current development progress
- **[⚙️ Operations](docs/04-operations/README.md)** - Operations and monitoring
- **[🚀 Setup Guide](docs/03-development/03-setup-guide/setup-guide.md)** - Environment setup instructions
- **[🔧 CLI Commands](docs/03-development/02-cli-commands-reference/cli-commands-reference.md)** - Command reference

### **Quick Links**
- **[Current Sprint](docs/03-development/01-project-management/current-sprint.md)** - Active development sprint
- **[API Contract](docs/02-architecture/05-api-contract/api-contract.md)** - API specifications
- **[Terraform Best Practices](docs/04-operations/terraform-best-practices-checklist.md)** - Infrastructure guidelines

---

**Navigation:**
🏠 **Home:** [Documentation Index](./README.md)

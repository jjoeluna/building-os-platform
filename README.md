# 🏢 BuildingOS Platform

**The central platform for intelligent building management** - A serverless, event-driven architecture that orchestrates building automation through AI-powered agents.

[![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)](https://terraform.io)
[![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 **Quick Start**

### **Prerequisites**
- AWS CLI configured with appropriate permissions
- Python 3.11+
- Terraform >= 1.5
- PowerShell (Windows) or Bash (Linux/Mac)

### **5-Minute Setup**
```bash
# 1. Clone the repository
git clone https://github.com/jjoeluna/building-os-platform.git
cd building-os-platform

# 2. Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\Activate.ps1  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure AWS credentials
aws configure

# 5. Deploy to development environment
cd terraform/environments/dev
terraform init
terraform plan
terraform apply
```

---

## 🏗️ **Architecture Overview**

BuildingOS is built on a **distributed agent architecture** that communicates asynchronously via AWS SNS topics. The system consists of specialized AI agents, each with unique responsibilities:

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

## 📁 **Project Structure**

```
building-os-platform/
├── 📖 docs/                          # Complete project documentation
│   ├── 00-business-context/          # Business requirements and context
│   ├── 01-project-vision/            # Project vision and goals
│   ├── 02-architecture/              # System architecture and design
│   ├── 03-development/               # Development tools and status
│   └── 04-operations/                # Operations and monitoring
├── 🏗️ terraform/                     # Infrastructure as Code
│   ├── environments/                 # Environment-specific configurations
│   │   ├── dev/                      # Development environment
│   │   ├── stg/                      # Staging environment
│   │   └── prd/                      # Production environment
│   └── modules/                      # Reusable Terraform modules
├── 🤖 src/                           # Application source code
│   ├── agents/                       # Lambda agent implementations
│   ├── tools/                        # Utility tools and scripts
│   └── layers/                       # Lambda layers (shared code)
├── 🧪 tests/                         # Test suites and test data
├── 🎨 frontend/                      # User interface components
└── 📋 scripts/                       # Automation and deployment scripts
```

---

## 🚀 **Development Workflow**

### **1. Environment Setup**
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### **2. Development Commands**
```bash
# Validate Terraform configuration
cd terraform/environments/dev
terraform validate

# Plan infrastructure changes
terraform plan

# Apply changes
terraform apply

# Test Lambda functions
pytest tests/

# Run integration tests
python tests/test_e2e_new_architecture.py
```

### **3. Deployment Process**
```bash
# Deploy to development
cd terraform/environments/dev
terraform apply

# Deploy to staging (after dev validation)
cd ../stg
terraform apply

# Deploy to production (after staging validation)
cd ../prd
terraform apply
```

---

## 📊 **Current Status**

### **Development Progress**
- ✅ **Fase 1: Fundamentals** - 100% Complete (8/8 items)
- ✅ **Fase 2: Structural** - 100% Complete (6/6 items)
- ✅ **Fase 3: Advanced** - 100% Complete (6/6 items)
- 🔄 **Fase 4: Compliance** - 75% Complete (3/4 items)
- ⏳ **Fase 5: Multi-Environment** - 0% Complete (0/3 items)

### **Key Achievements**
- ✅ **10 Lambda functions** migrated to modular architecture
- ✅ **Event-driven architecture** implemented with SNS topics
- ✅ **Infrastructure as Code** with Terraform modules
- ✅ **Observability** with CloudWatch and X-Ray
- ✅ **Multi-environment** support (dev/stg/prd)
- ✅ **Security & Encryption** with KMS keys and CloudTrail
- ✅ **VPC & Networking** with private subnets and VPC endpoints
- ✅ **Compliance Tags** with data classification and lifecycle policies

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Required environment variables
export TF_VAR_environment="dev"        # Environment (dev/stg/prd)
export TF_VAR_aws_region="us-east-1"   # AWS region
export TF_VAR_project_name="BuildingOS" # Project name
```

### **AWS Configuration**
```bash
# Configure AWS CLI
aws configure set aws_access_key_id YOUR_ACCESS_KEY
aws configure set aws_secret_access_key YOUR_SECRET_KEY
aws configure set default.region us-east-1
aws configure set default.output json
```

---

## 🧪 **Testing**

### **Test Categories**
- **Unit Tests** - Individual component testing
- **Integration Tests** - End-to-end workflow testing
- **Infrastructure Tests** - Terraform validation and testing
- **Performance Tests** - Load and stress testing

### **Running Tests**
```bash
# Run all tests
pytest

# Run specific test category
pytest tests/agents/
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

---

## 📚 **Documentation**

### **Essential Documentation**
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

## 🤝 **Contributing**

### **Development Process**
1. **Check current sprint** - Review [Development Status](docs/03-development/01-project-management/README.md)
2. **Follow architecture** - Adhere to [Solution Architecture](docs/02-architecture/01-solution-architecture/solution-architecture.md)
3. **Update documentation** - Keep docs in sync with code changes
4. **Test thoroughly** - Run tests before submitting changes
5. **Use AI assistance** - Leverage [AI Prompts](docs/03-development/98-ai-prompts/README.md)

### **Code Standards**
- **Language:** All code, comments, and documentation in English
- **Style:** Follow PEP 8 for Python code
- **Documentation:** Update relevant docs with code changes
- **Testing:** Write tests for new functionality
- **Commits:** Use descriptive commit messages

---

## 🚨 **Troubleshooting**

### **Common Issues**
- **Terraform errors** - Check [CLI Commands Reference](docs/03-development/02-cli-commands-reference/cli-commands-reference.md)
- **AWS permissions** - Verify IAM roles and policies
- **Environment issues** - Ensure correct environment variables
- **Dependency problems** - Check Python virtual environment

### **Getting Help**
1. **Check documentation** - Review relevant docs first
2. **Search issues** - Look for similar problems
3. **Review logs** - Check CloudWatch logs for errors
4. **Ask for help** - Create an issue with detailed information

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🏆 **Acknowledgments**

- **AWS** - Cloud infrastructure and services
- **Terraform** - Infrastructure as Code
- **Python** - Programming language
- **Community** - Contributors and supporters

---

**🚀 Ready to build the future of intelligent building management? Start with the [Setup Guide](docs/03-development/03-setup-guide/setup-guide.md)!**

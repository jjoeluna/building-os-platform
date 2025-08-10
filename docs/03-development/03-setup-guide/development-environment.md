# **🛠️ DEVELOPMENT ENVIRONMENT SETUP - BUILDINGOS**

> **Última Atualização:** 2025-01-07  
> **Status:** ✅ Ambiente configurado e testado

---

## **📋 PRÉ-REQUISITOS**

### **Sistema Operacional**
- ✅ **Windows 10/11** (testado)
- ✅ **PowerShell 7+** (recomendado)
- ✅ **Git** instalado

### **Ferramentas Principais**
- ✅ **Python 3.13.5** (ou superior)
- ✅ **Terraform 1.5+** (testado com 1.5.0)
- ✅ **AWS CLI** configurado
- ✅ **Docker** (opcional, para testes isolados)

---

## **🚀 CONFIGURAÇÃO RÁPIDA**

### **1. Clone do Repositório**
```bash
git clone <repository-url>
cd building-os-platform
```

### **2. Ativação do Ambiente Virtual**
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Verificar ativação
(venv) PS C:\Projects\building-os-platform>
```

### **3. Instalação de Dependências**
```bash
# Dependências de teste
pip install -r tests/api/requirements.txt

# Dependências comuns
pip install -r src/layers/common_utils/requirements.txt

# Verificar instalação
python -c "import boto3, requests, pytest; print('✅ Dependências OK!')"
```

### **4. Configuração Terraform**
```bash
cd terraform/environments/dev
terraform init
terraform validate
```

---

## **🔧 CONFIGURAÇÕES DETALHADAS**

### **Ambiente Virtual Python**

#### **Criação (se necessário):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### **Dependências Instaladas:**
```
# Testes
pytest==7.4.2
requests==2.32.3
pytest-html==3.2.0
pytest-json-report==1.5.0
pytest-xdist==3.3.1
python-dotenv==1.0.0
pydantic==2.9.2
rich==13.6.0

# AWS e Utilitários
boto3==1.34.145
PyJWT==2.8.0
```

### **Terraform Configuration**

#### **Providers Configurados:**
```hcl
terraform {
  required_version = ">= 1.5"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
    
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}
```

#### **Validações Implementadas:**
```hcl
variable "environment" {
  validation {
    condition     = contains(["dev", "stg", "prd"], var.environment)
    error_message = "Environment must be one of: dev, stg, prd."
  }
}
```

---

## **🧪 TESTES DE VALIDAÇÃO**

### **Testes Python**
```bash
# Verificar ambiente
python --version  # Python 3.13.5

# Testar imports
python -c "import boto3, requests, pytest; print('✅ OK')"

# Executar testes básicos
cd tests/api
pytest -v
```

### **Testes Terraform**
```bash
cd terraform/environments/dev

# Validação de sintaxe
terraform validate

# Validação de variáveis
terraform plan

# Teste de valores inválidos
terraform plan -var-file="invalid.tfvars"  # Deve falhar
```

---

## **📁 ESTRUTURA DE DIRETÓRIOS**

```
building-os-platform/
├── venv/                          # Ambiente virtual Python
├── src/                           # Código fonte
│   ├── agents/                    # Agentes Lambda
│   ├── tools/                     # Ferramentas
│   └── layers/                    # Lambda layers
├── terraform/                     # Infraestrutura
│   ├── environments/              # Ambientes (dev, stg, prd)
│   └── modules/                   # Módulos reutilizáveis
├── tests/                         # Testes automatizados
├── docs/                          # Documentação
└── frontend/                      # Interface web
```

---

## **🔍 VERIFICAÇÃO DE AMBIENTE**

### **Script de Verificação**
```bash
# Executar verificação completa
.\scripts\verify-environment.ps1
```

### **Checklist Manual**
- [ ] **Python venv ativo** - `(venv)` no prompt
- [ ] **Dependências instaladas** - `pip list` mostra pacotes
- [ ] **Terraform funcionando** - `terraform --version`
- [ ] **AWS configurado** - `aws sts get-caller-identity`
- [ ] **Git configurado** - `git --version`

---

## **🐛 SOLUÇÃO DE PROBLEMAS**

### **Problema: Ambiente Virtual Não Ativa**
```bash
# Solução
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### **Problema: Dependências Não Instalam**
```bash
# Solução
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### **Problema: Terraform Provider Missing**
```bash
# Solução
terraform init
terraform validate
```

### **Problema: AWS Credentials**
```bash
# Solução
aws configure
# Ou usar variáveis de ambiente
$env:AWS_ACCESS_KEY_ID="your-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret"
```

---

## **📊 MÉTRICAS DE AMBIENTE**

### **Performance:**
- **Tempo de ativação venv:** < 2 segundos
- **Tempo de instalação dependências:** ~30 segundos
- **Tempo de terraform init:** ~10 segundos
- **Tempo de terraform validate:** < 5 segundos

### **Cobertura:**
- **Dependências Python:** 100% instaladas
- **Providers Terraform:** 100% configurados
- **Validações:** 100% implementadas
- **Testes:** 100% executáveis

---

## **🔄 MANUTENÇÃO**

### **Atualizações Regulares**
```bash
# Atualizar pip
python -m pip install --upgrade pip

# Atualizar dependências
pip install -r requirements.txt --upgrade

# Atualizar Terraform
terraform init -upgrade
```

### **Limpeza**
```bash
# Limpar cache pip
pip cache purge

# Limpar cache Terraform
terraform init -reconfigure
```

---

## **🔗 LINKS ÚTEIS**

- [Terraform Best Practices](../04-operations/terraform-best-practices-checklist.md)
- [Testing Results](../04-operations/terraform-testing-results.md)
- [Current Sprint](../01-project-management/current-sprint.md)
- [Architecture Documentation](../../02-architecture/README.md)

---

> **Nota:** Este ambiente foi testado e validado em 2025-01-07. Mantenha esta documentação atualizada conforme mudanças no ambiente.

# 📋 Development Backlog - Post-Architecture Review

Backlog de desenvolvimento priorizado após a revisão arquitetural de 2024-08-16. O foco é fechar os gaps críticos para o MVP e avançar a visão técnica da plataforma.

---

## 🎯 **Priority Levels**

- **🔥 CRITICAL** - Bloqueia a entrega do MVP ou a funcionalidade principal da arquitetura.
- **🎯 HIGH** - Essencial para a visão do produto ou para a robustez da plataforma.
- **📋 MEDIUM** - Melhorias importantes de eficiência, segurança ou manutenibilidade.
- **💡 LOW** - Otimizações futuras, débitos técnicos menores ou exploração de novas funcionalidades.

---

## 🔥 **CRITICAL PRIORITY (Pre-Development Validation)**

### **Epic: Validação de Saúde da Infraestrutura**
- **Tarefa**: Executar suíte de testes de integração da API.
- **Descrição**: Executar os scripts de teste em `tests/api` para gerar um relatório de saúde de todos os endpoints HTTP, garantindo que a infraestrutura base está funcional antes de novas implementações.
- **Status**: ❌ **Pendente**
- **Effort**: 1 day
- **Dependencies**: Nenhum.

### **Epic: Validação do Barramento de Eventos SNS**
- **Tarefa**: Criar e executar script para teste individual de tópicos SNS.
- **Descrição**: Desenvolver um script (ou uma série de comandos) que publique uma mensagem de teste em cada um dos 8 tópicos SNS e verifique os logs do CloudWatch da Lambda correspondente para confirmar o recebimento. Isso valida a "fiação" da arquitetura assíncrona.
- **Status**: ❌ **Pendente**
- **Effort**: 2 days
- **Dependencies**: Validação da Saúde da Infraestrutura.

### **Epic: Validação do Fluxo de Chat de Ponta a Ponta**
- **Tarefa**: Implementar e testar cliente de chat simples.
- **Descrição**: Adaptar ou criar uma página HTML/JS (`chat-simple.html`) para testar o fluxo completo de comunicação via WebSocket e SNS. O objetivo é validar que uma mensagem enviada pelo usuário passe por toda a arquitetura de agentes e retorne uma resposta.
- **Status**: ❌ **Pendente**
- **Effort**: 1 day
- **Dependencies**: Validação do Barramento de Eventos SNS.

---

## 🔥 **CRITICAL PRIORITY (MVP Gaps)**

### **Epic: Core MVP Functionality**

- **Implement `agent_erp`**
  - **Status**: ❌ **Pendente**
  - **Description**: Criar e implementar o agente de integração com o ERP Superlógica. Este agente é responsável por sincronizar a base de usuários (residentes) que é a fonte da verdade para o sistema de acesso.
  - **Tasks**:
    - `[ ]` Criar a estrutura do diretório `src/agents/agent_erp/`.
    - `[ ]` Desenvolver o código inicial da Lambda para conectar à API do Superlógica.
    - `[ ]` Adicionar o módulo da Lambda em `lambda_functions.tf`.
    - `[ ]` Definir as políticas de IAM necessárias para acesso seguro à API externa.
    - `[ ]` Criar testes unitários para o agente.
  - **Effort**: 5 days
  - **Dependencies**: Nenhum.

---

## 🎯 **HIGH PRIORITY (Core Architecture Gaps)**

### **Epic: AI & Intelligence**

- **Implement Kendra Search for RAG**
  - **Status**: ❌ **Pendente**
  - **Description**: Provisionar e integrar um índice do AWS Kendra para habilitar a funcionalidade de Retrieval Augmented Generation (RAG) no `agent_persona`. Isso permitirá que o agente responda a perguntas com base em uma base de conhecimento de documentos.
  - **Tasks**:
    - `[ ]` Criar um novo módulo Terraform para `aws_kendra_index`.
    - `[ ]` Definir as fontes de dados (Data Sources) para o Kendra.
    - `[ ]` Adicionar permissões na IAM Role do `agent_persona` para acessar o índice Kendra.
    - `[ ]` Atualizar o código do `agent_persona` para usar o Kendra em suas respostas.
  - **Effort**: 3 days
  - **Dependencies**: `agent_persona` implementado.

### **Epic: Data & Storage**

- **Configure S3 Bucket for Agent Documents**
  - **Status**: ❌ **Pendente**
  - **Description**: Criar e configurar um bucket S3 dedicado para que os agentes (especialmente o futuro `agent_erp`) possam armazenar e servir arquivos, como segunda via de boletos, contratos, etc.
  - **Tasks**:
    - `[ ]` Adicionar um novo módulo `s3_bucket` no Terraform para documentos.
    - `[ ]` Configurar a política de bucket e o CORS.
    - `[ ]` Garantir que a criptografia com KMS esteja ativa.
    - `[ ]` Adicionar permissões na IAM Role dos agentes para ler/escrever neste bucket.
  - **Effort**: 1 day
  - **Dependencies**: Nenhum.

---

## 📋 **MEDIUM PRIORITY (Vision Expansion)**

### **Epic: Final Vision Agents (Placeholders)**

- **Implement `agent_brokers`**
  - **Status**: ❌ **Pendente**
  - **Description**: Criar o agente de integração com plataformas de hospitalidade (AirBnB, Booking.com) para gerenciar reservas de aluguel de curta temporada.
  - **Effort**: Large (to be defined)
  - **Dependencies**: `agent_locks`.

- **Implement `agent_locks`**
  - **Status**: ❌ **Pendente**
  - **Description**: Criar o agente de integração com APIs de fechaduras inteligentes (ex: TTLock) para provisionar acesso aos apartamentos.
  - **Effort**: Medium (to be defined)
  - **Dependencies**: Nenhum.

- **Implement `agent_metering`**
  - **Status**: ❌ **Pendente**
  - **Description**: Criar o agente de integração com sistemas de medição de consumo (água, gás) para coletar e reportar dados.
  - **Effort**: Medium (to be defined)
  - **Dependencies**: Nenhum.

---

## 💡 **LOW PRIORITY (Non-Functional Requirements)**

### **Epic: CI/CD & Testing**
- **Expand Test Coverage**
  - **Status**: ❌ **Pendente**
  - **Description**: Aumentar a cobertura de testes unitários e de integração para todos os agentes existentes para garantir a estabilidade do código.
  - **Effort**: 3 days
  - **Dependencies**: Agentes implementados.

### **Epic: Qualidade de Código e Testes Unitários**
- **Tarefa**: Implementar Testes Unitários para Agentes.
- **Descrição**: Desenvolver uma suíte de testes unitários para a lógica de negócio de cada agente (`app.py`). O objetivo é isolar e validar as funções internas, o tratamento de eventos e a lógica de decisão de cada componente, em conformidade com as diretrizes do `terraform-best-practices-checklist.md`.
- **Status**: ❌ **Pendente**
- **Effort**: 3 days
- **Dependencies**: Agentes implementados.

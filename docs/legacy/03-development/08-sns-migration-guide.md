# Guia de Migração SNS: Legacy → Arquitetura Padronizada

## 📋 Resumo da Migração

Este documento descreve a migração da arquitetura SNS legacy para a nova arquitetura padronizada conforme definido na documentação de solução.

## 🎯 Objetivos

- ✅ Implementar nomenclatura padronizada para tópicos SNS
- ✅ Criar fluxo de mensagens mais claro e estruturado
- ✅ Manter compatibilidade durante a transição
- ✅ Preparar para implementação do WebSocket real-time

## 📊 Mapeamento de Tópicos

### Arquitetura Legacy vs. Nova

| **Fluxo** | **Legacy** | **Nova Arquitetura** | **Publisher** | **Subscriber** |
|-----------|------------|---------------------|---------------|----------------|
| Chat → Persona | *(API direto)* | `bos-chat-intention-topic` | Chat Lambda | Agent Persona |
| Persona → Director | `intention_topic` | `bos-persona-intention-topic` | Agent Persona | Agent Director |
| Director → Coordinator | `mission_topic` | `bos-director-mission-topic` | Agent Director | Agent Coordinator |
| Coordinator → Agents | *(invocação direta)* | `bos-coordinator-task-topic` | Agent Coordinator | Integration Agents |
| Agents → Coordinator | `task_result_topic` | `bos-agent-task-result-topic` | Integration Agents | Agent Coordinator |
| Coordinator → Director | `mission_result_topic` | `bos-coordinator-mission-result-topic` | Agent Coordinator | Agent Director |
| Director → Persona | `intention_result_topic` | `bos-director-response-topic` | Agent Director | Agent Persona |
| Persona → Chat | *(API direto)* | `bos-persona-response-topic` | Agent Persona | Chat Lambda |

## 🔧 Mudanças no Terraform

### ✅ Já Implementado

1. **Novos tópicos SNS criados** com nomenclatura padronizada
2. **Subscriptions SNS** configuradas para todos os fluxos
3. **Permissões IAM** atualizadas para incluir novos tópicos
4. **Variáveis de ambiente** dos Lambdas incluem novos tópicos
5. **Tópicos legacy mantidos** para compatibilidade

### 📋 Próximos Passos

1. **Atualizar código dos agentes** para usar novos tópicos
2. **Testar fluxo completo** com nova arquitetura
3. **Remover tópicos legacy** após validação
4. **Implementar Chat Lambda** para WebSocket

## 🛠 Mudanças Necessárias no Código

### Agent Persona (`src/agents/agent_persona/app.py`)

**Variáveis de ambiente adicionadas:**
```python
# Novos tópicos
PERSONA_INTENTION_TOPIC_ARN = os.environ.get("PERSONA_INTENTION_TOPIC_ARN")
DIRECTOR_RESPONSE_TOPIC_ARN = os.environ.get("DIRECTOR_RESPONSE_TOPIC_ARN") 
PERSONA_RESPONSE_TOPIC_ARN = os.environ.get("PERSONA_RESPONSE_TOPIC_ARN")
```

**Mudanças no fluxo:**
- ✅ Continua recebendo via `intention_result_topic` (legacy)
- 🆕 Deve escutar também `director_response_topic` (novo)
- 🆕 Publicar em `persona_intention_topic` em vez de `intention_topic`

### Agent Director (`src/agents/agent_director/app.py`)

**Variáveis de ambiente adicionadas:**
```python
# Novos tópicos
DIRECTOR_MISSION_TOPIC_ARN = os.environ.get("DIRECTOR_MISSION_TOPIC_ARN")
DIRECTOR_RESPONSE_TOPIC_ARN = os.environ.get("DIRECTOR_RESPONSE_TOPIC_ARN")
COORDINATOR_MISSION_RESULT_TOPIC_ARN = os.environ.get("COORDINATOR_MISSION_RESULT_TOPIC_ARN")
```

**Mudanças no fluxo:**
- ✅ Continua recebendo via `intention_topic` (legacy)
- 🆕 Deve escutar também `persona_intention_topic` (novo)
- 🆕 Publicar em `director_mission_topic` em vez de `mission_topic`
- 🆕 Publicar em `director_response_topic` em vez de `intention_result_topic`

### Agent Coordinator (`src/agents/agent_coordinator/app.py`)

**Variáveis de ambiente adicionadas:**
```python
# Novos tópicos
COORDINATOR_TASK_TOPIC_ARN = os.environ.get("COORDINATOR_TASK_TOPIC_ARN")
AGENT_TASK_RESULT_TOPIC_ARN = os.environ.get("AGENT_TASK_RESULT_TOPIC_ARN")
COORDINATOR_MISSION_RESULT_TOPIC_ARN = os.environ.get("COORDINATOR_MISSION_RESULT_TOPIC_ARN")
```

**Mudanças no fluxo:**
- ✅ Continua recebendo via `mission_topic` (legacy)
- 🆕 Deve escutar também `director_mission_topic` (novo)
- 🆕 Publicar tarefas em `coordinator_task_topic` em vez de invocar diretamente
- 🆕 Escutar resultados via `agent_task_result_topic` em vez de `task_result_topic`
- 🆕 Publicar em `coordinator_mission_result_topic` em vez de `mission_result_topic`

### Integration Agents (Elevator, PSIM, etc.)

**Variáveis de ambiente adicionadas:**
```python
# Novo tópico
AGENT_TASK_RESULT_TOPIC_ARN = os.environ.get("AGENT_TASK_RESULT_TOPIC_ARN")
```

**Mudanças no fluxo:**
- 🆕 Receber tarefas via `coordinator_task_topic` (SNS) em vez de invocação direta
- 🆕 Publicar resultados em `agent_task_result_topic` em vez de `task_result_topic`

## 🔄 Estratégia de Migração

### Fase 1: Preparação (✅ Concluída)
- ✅ Terraform atualizado com novos tópicos
- ✅ Variáveis de ambiente configuradas
- ✅ Permissões SNS criadas

### Fase 2: Implementação Gradual
1. **Atualizar Agent Persona** para usar novos tópicos mantendo compatibility
2. **Atualizar Agent Director** com dual-mode (legacy + novo)
3. **Atualizar Agent Coordinator** com dual-mode
4. **Atualizar Integration Agents** para escutar novos tópicos

### Fase 3: Validação
1. **Testes end-to-end** com nova arquitetura
2. **Monitoramento** de ambos os fluxos
3. **Verificação** de performance e confiabilidade

### Fase 4: Limpeza
1. **Remover** código legacy dos agentes
2. **Remover** tópicos legacy do Terraform
3. **Implementar** Chat Lambda para WebSocket

## 🧪 Testes Recomendados

### Teste 1: Fluxo Completo Legacy
```bash
# Validar que fluxo atual continua funcionando
curl -X POST [API]/persona -d '{"message": "chame o elevador para o térreo"}'
```

### Teste 2: Fluxo Parcial Novo
```bash
# Após implementar Agent Persona com novos tópicos
# Verificar logs do CloudWatch para confirmar publicação nos novos tópicos
```

### Teste 3: Fluxo Completo Novo
```bash
# Após migração completa
# Validar que mensagem percorre toda nova arquitetura
```

## 📈 Métricas de Sucesso

- ✅ **Zero downtime** durante migração
- ✅ **Mesma latência** ou melhor que arquitetura legacy
- ✅ **Logs claros** mostrando fluxo através dos novos tópicos
- ✅ **Mensagens processadas** sem perda ou duplicação
- ✅ **Compatibilidade** mantida até limpeza final

## 🚨 Pontos de Atenção

1. **Ordem de migração**: Persona → Director → Coordinator → Integration Agents
2. **Dual-mode temporário**: Agentes devem processar ambos os fluxos
3. **Monitoring**: Acompanhar métricas de ambas as arquiteturas
4. **Rollback**: Manter capacidade de voltar para legacy se necessário
5. **WebSocket**: Preparar para adição do Chat Lambda no futuro

## 📚 Documentação Relacionada

- `docs/02-architecture/01-solution-architecture.md` - Arquitetura completa
- `docs/03-development/07-api-status-baseline.md` - Status atual da API
- `terraform/environments/dev/main.tf` - Configuração de infraestrutura

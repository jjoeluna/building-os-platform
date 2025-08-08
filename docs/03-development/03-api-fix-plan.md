# 🛠️ Plano de Correção de APIs - BuildingOS

**Data:** 7 de Agosto de 2025  
**Baseado em:** Relatório de testes Python com pytest  
**Status Atual:** 13/24 testes passando (54% de sucesso)

---

## 📊 **ANÁLISE DOS PROBLEMAS IDENTIFICADOS**

### **Categoria 1: Problemas Críticos (Bloqueadores)**
- ❌ **Elevator API**: Erros 500 contínuos
- ❌ **Persona Conversations**: Erros 500 contínuos  
- ⚠️ **Status Code Inconsistente**: Persona retorna 202 em vez de 200

### **Categoria 2: Problemas de Infraestrutura**
- ❌ **CORS Headers**: Ausentes em todos os endpoints
- ⚠️ **Coordinator 404**: Missões inexistentes retornam 404 esperado

### **Categoria 3: Problemas de Configuração**
- ⚠️ **Performance**: Director com ~5-6s de resposta
- ⚠️ **Validação**: Alguns endpoints rejeitam payloads válidos

---

## 🛠️ **FERRAMENTAS DE DIAGNÓSTICO E TESTE**

### **📊 `diagnose_api.py` - Diagnóstico Rápido**
**Uso:** Troubleshooting rápido e análise de logs AWS
```bash
python diagnose_api.py
```
**Características:**
- ⚡ Execução rápida (~30s)
- 🔍 Integração com CloudWatch logs
- 🎯 Priorização automática de problemas
- 📈 Análise de performance em tempo real
- 🚨 Identificação de erros críticos

**Output:** Relatório consolidado em `reports/api_diagnosis_TIMESTAMP.json`

### **🧪 `run_tests.py` - Suite Completa**
**Uso:** Validação completa e relatórios detalhados
```bash
python run_tests.py
```
**Características:**
- 🔬 24 testes estruturados com pytest
- 📊 Relatórios HTML e JSON detalhados
- 🔄 Retry logic e timeouts configuráveis
- 📋 Métricas de qualidade e performance
- 🎨 Formatação rica com Rich library

**Output:** Relatórios em `api-test-results-TIMESTAMP.json` + HTML

### **⚡ Estratégia de Uso Combinado**

| Momento | Ferramenta | Objetivo |
|---------|------------|----------|
| 🚀 **Início** | `diagnose_api.py` | Mapear problemas atuais |
| 📏 **Baseline** | `run_tests.py` | Linha de base detalhada |
| 🔧 **Durante Dev** | `diagnose_api.py` | Verificação rápida de mudanças |
| ✅ **Pós-Correção** | Ambas | Validação completa |
| 🚀 **Pós-Deploy** | `run_tests.py` | Confirmação final |

---

## 🎯 **PLANO DE CORREÇÃO - 4 FASES**

---

## **FASE 1: CORREÇÕES CRÍTICAS** ⏰ *Estimativa: 2-3 horas*

### **1.1 Corrigir Elevator API (PRIORIDADE MÁXIMA)**

**Problema:** Erros 500 em todos os requests para `/elevator/call`

**Ações:**
```bash
# 1. Verificar logs do Lambda
aws logs filter-log-events --log-group-name "/aws/lambda/bos-agent-elevator-dev" --start-time $(date -d '1 hour ago' +%s)000

# 2. Testar endpoint diretamente
curl -X POST "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/elevator/call" \
  -H "Content-Type: application/json" \
  -d '{"mission_id":"test-123","action":"check_status"}'
```

**Investigação:**
- [ ] Verificar se handler está recebendo `mission_id` corretamente
- [ ] Validar estrutura do payload esperado vs recebido
- [ ] Verificar dependências/importações no código
- [ ] Testar handler isoladamente

**Correção Esperada:**
```python
# Em src/agents/agent_elevator/app.py
def handle_api_request(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        mission_id = body.get('mission_id')
        
        if not mission_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'mission_id is required'})
            }
        # ... resto do handler
```

### **1.2 Corrigir Persona Conversations (PRIORIDADE ALTA)**

**Problema:** Erros 500 em `/persona/conversations`

**Ações:**
```bash
# 1. Verificar logs específicos
aws logs filter-log-events --log-group-name "/aws/lambda/bos-agent-persona-dev" --filter-pattern "conversations"

# 2. Testar com diferentes user_ids
curl "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/persona/conversations?user_id=test-user"
```

**Investigação:**
- [ ] Verificar se rota está configurada corretamente no API Gateway
- [ ] Validar consulta ao DynamoDB para histórico de conversas
- [ ] Verificar permissões IAM para tabela de memória

### **1.3 Padronizar Status Codes**

**Problema:** Persona retorna 202 em vez de 200

**Ação:**
```python
# Alterar em src/agents/persona_agent/app.py
return {
    'statusCode': 200,  # Era 202
    'body': json.dumps({
        'message': 'Request received. The Director is analyzing the intention.',
        'session_id': session_id
    })
}
```

---

## **FASE 2: INFRAESTRUTURA E CORS** ⏰ *Estimativa: 1-2 horas*

### **2.1 Implementar CORS Headers Globalmente**

**Problema:** Nenhum endpoint retorna headers CORS

**Solução:** Modificar todos os handlers para incluir CORS

**Template para todos os handlers:**
```python
def create_cors_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
            'Access-Control-Max-Age': '86400'
        },
        'body': json.dumps(body) if isinstance(body, dict) else body
    }
```

**Arquivos para Modificar:**
- [ ] `src/agents/health_check/app.py`
- [ ] `src/agents/director/app.py`
- [ ] `src/agents/persona_agent/app.py`
- [ ] `src/agents/agent_elevator/app.py`
- [ ] `src/agents/agent_psim/app.py`
- [ ] `src/agents/coordinator/app.py`

### **2.2 Adicionar Handler OPTIONS para Preflight**

**Implementação em cada handler:**
```python
def lambda_handler(event, context):
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return create_cors_response(200, '')
    
    # ... resto do código
```

---

## **FASE 3: OTIMIZAÇÃO E PERFORMANCE** ⏰ *Estimativa: 2-3 horas*

### **3.1 Otimizar Performance do Director**

**Problema:** Tempo de resposta de 5-6 segundos

**Investigação:**
```bash
# Análise de performance detalhada
aws logs filter-log-events --log-group-name "/aws/lambda/bos-agent-director-dev" --filter-pattern "Duration"
```

**Ações:**
- [ ] Verificar cold start vs warm start
- [ ] Otimizar conexões com Bedrock/DynamoDB
- [ ] Implementar connection pooling
- [ ] Revisar timeout configurations

### **3.2 Melhorar Validação de Payloads**

**Implementar validação consistente:**
```python
from pydantic import BaseModel, ValidationError

class ElevatorRequest(BaseModel):
    mission_id: str
    action: str
    parameters: dict = {}

def validate_request(body, model_class):
    try:
        return model_class(**body), None
    except ValidationError as e:
        return None, {'error': 'Invalid payload', 'details': e.errors()}
```

---

## **FASE 4: TESTES E VALIDAÇÃO** ⏰ *Estimativa: 1 hora*

### **4.1 Atualizar Testes Para Refletir Correções**

**Modificar expectativas de teste:**
```python
# Em test_endpoints.py
def test_persona_valid_message(self):
    payload = TestPayloads.persona_message()
    response, data = client.post("/persona", json=payload)
    assert response.status_code == 200  # Era 202
    
def test_cors_headers_present(self, endpoint):
    # Atualizar para verificar headers específicos
    assert response.headers.get('Access-Control-Allow-Origin') == '*'
```

### **4.2 Executar Testes de Regressão**

```bash
# Suite completa
python -m pytest test_endpoints.py -v --html=reports/post-fix-report.html

# Testes específicos por endpoint
python -m pytest test_endpoints.py::TestElevatorEndpoint -v
python -m pytest test_endpoints.py::TestPersonaEndpoint -v
python -m pytest test_endpoints.py::TestCORSHeaders -v
```

---

## 📋 **CHECKLIST DE EXECUÇÃO OTIMIZADO**

### **Pré-requisitos**
- [ ] Ambiente virtual ativo (`.venv`)
- [ ] AWS CLI configurado
- [ ] Terraform state atualizado
- [ ] Backup do código atual
- [ ] **Diagnóstico inicial**: `python diagnose_api.py`
- [ ] **Baseline completo**: `python run_tests.py`

### **Fase 1 - Correções Críticas**
- [ ] **Elevator API:**
  - [ ] Investigar logs: `python diagnose_api.py` (foco CloudWatch)
  - [ ] Corrigir handler do Elevator
  - [ ] Validar: `python -m pytest test_endpoints.py::TestElevatorEndpoint -v`
- [ ] **Persona Conversations:**
  - [ ] Investigar logs do Persona
  - [ ] Corrigir rota de conversations
  - [ ] Validar: `python -m pytest test_endpoints.py::TestPersonaEndpoint -v`
- [ ] **Status Codes:**
  - [ ] Alterar status code do Persona (202→200)
  - [ ] Confirmar: `python diagnose_api.py`
- [ ] **Deploy**: `terraform apply -auto-approve`
- [ ] **Validação Fase 1**: `python run_tests.py`

### **Fase 2 - CORS**
- [ ] Criar função utilitária `create_cors_response`
- [ ] Modificar todos os 6 handlers
- [ ] Adicionar handlers OPTIONS
- [ ] **Teste CORS**: `python -m pytest test_endpoints.py::TestCORSHeaders -v`
- [ ] **Deploy**: `terraform apply -auto-approve`
- [ ] **Validação CORS**: `python diagnose_api.py`

### **Fase 3 - Performance**
- [ ] Analisar métricas: `python diagnose_api.py` (foco performance)
- [ ] Otimizar código do Director
- [ ] Implementar validação com Pydantic
- [ ] **Teste Performance**: `python run_tests.py` (análise tempos)

### **Fase 4 - Validação Final**
- [ ] Atualizar expectativas de teste
- [ ] **Suite Completa**: `python run_tests.py`
- [ ] **Diagnóstico Final**: `python diagnose_api.py`
- [ ] **Comparar Resultados**: Baseline vs Final
- [ ] Documentar mudanças e métricas alcançadas

---

## 🎯 **CRITÉRIOS DE SUCESSO**

**Meta:** Atingir 90%+ de testes passando (21/24 testes)

### **Resultados Esperados Pós-Correção:**
- ✅ **Elevator API**: 0 erros 500
- ✅ **Persona Conversations**: Funcionando corretamente
- ✅ **Status Codes**: Consistentes (200 para sucesso)
- ✅ **CORS Headers**: Presentes em todos os endpoints
- ✅ **Performance**: Director < 3s de resposta
- ✅ **Coordinator**: Comportamento 404 mantido (correto)

### **Métricas de Qualidade:**
- Response time médio < 2s (exceto Director < 3s)
- Error rate < 5%
- CORS compliance 100%
- Status code consistency 100%

---

## 🚀 **COMANDOS DE EXECUÇÃO OTIMIZADA**

### **🔧 Setup Inicial**
```bash
# 1. Ativar ambiente e ir para testes
.\.venv\Scripts\Activate.ps1
cd tests\api

# 2. Diagnóstico inicial rápido + logs AWS
python diagnose_api.py

# 3. Baseline completo com pytest
python run_tests.py
```

### **⚡ Durante Desenvolvimento (Ciclo Rápido)**
```bash
# Diagnóstico rápido após mudanças
python diagnose_api.py

# Testes específicos para validar correções
python -m pytest test_endpoints.py::TestElevatorEndpoint -v
python -m pytest test_endpoints.py::TestPersonaEndpoint -v
python -m pytest test_endpoints.py::TestCORSHeaders -v
```

### **🚀 Deploy e Validação Completa**
```bash
# 1. Deploy das correções
cd ..\..\terraform\environments\dev
terraform apply -auto-approve

# 2. Validação pós-deploy
cd ..\..\tests\api
python diagnose_api.py  # Verificação rápida
python run_tests.py     # Suite completa com relatórios

# 3. Comparação de resultados
python -c "
import json
with open('reports/api_diagnosis_*.json') as f: diag = json.load(f)
with open('api-test-results-*.json') as f: tests = json.load(f)
print(f'Diagnóstico: {diag[\"summary\"][\"success_rate\"]}% | Testes: {tests[\"summary\"][\"success_rate\"]}%')
"
```

### **📊 Fluxo por Fase**
```bash
# FASE 1: Correções Críticas
python diagnose_api.py                                    # → Identifica problemas
python -m pytest test_endpoints.py::TestElevatorEndpoint # → Valida Elevator
python -m pytest test_endpoints.py::TestPersonaEndpoint  # → Valida Persona

# FASE 2: CORS  
python diagnose_api.py                                    # → Verifica CORS
python -m pytest test_endpoints.py::TestCORSHeaders      # → Valida CORS

# FASE 3: Performance
python diagnose_api.py                                    # → Monitora performance
python run_tests.py                                       # → Relatório completo

# FASE 4: Validação Final
python run_tests.py                                       # → Suite completa final
```

---

**🔄 Próximos Passos:** Começar pela **Fase 1** - Correções Críticas, focando primeiro no Elevator API que está com 100% de falha nos testes.

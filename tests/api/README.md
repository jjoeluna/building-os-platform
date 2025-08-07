# BuildingOS API Testing Suite

Suíte abrangente de testes para as APIs do BuildingOS com capacidades de diagnóstico rápido e validação completa.

## 🚀 Início Rápido

```bash
# Do diretório raiz do projeto
.\tests\api\quick_setup.ps1  # Setup automático + diagnóstico rápido
```

## �️ Visão Geral das Ferramentas

### 🔍 `diagnose_api.py` - Diagnóstico Rápido
**Propósito:** Troubleshooting rápido e análise de logs AWS  
**Duração:** ~30 segundos  
**Caso de Uso:** Loop de feedback durante desenvolvimento

```bash
python diagnose_api.py
```

**Recursos:**
- ⚡ Teste rápido de endpoints
- 📋 Integração com logs do CloudWatch  
- 🎯 Priorização automática de problemas
- 📊 Métricas de performance em tempo real
- 🚨 Identificação de issues críticas

### 🧪 `run_tests.py` - Testes Abrangentes
**Propósito:** Validação completa e relatórios detalhados  
**Duração:** ~2-3 minutos  
**Caso de Uso:** Validação completa e documentação

```bash
python run_tests.py
```

**Recursos:**
- 🔬 24 casos de teste estruturados com pytest
- 📈 Relatórios detalhados em HTML e JSON
- 🔄 Lógica de retry e handling de timeouts
- 📊 Métricas de qualidade e análise de performance
- 🎨 Output rico no console com tracking de progresso

## ⚡ Fluxo de Desenvolvimento Otimizado

### Estratégia por Fase de Desenvolvimento

| Fase | Ferramenta Principal | Ferramenta Secundária | Propósito |
|------|---------------------|----------------------|-----------|
| **Diagnóstico Inicial** | `diagnose_api.py` | - | Mapear issues atuais |
| **Loop de Desenvolvimento** | `diagnose_api.py` | pytest específico | Feedback rápido |
| **Pós-Implementação** | `run_tests.py` | `diagnose_api.py` | Validação completa |
| **Pré-Deploy** | Ambas | - | Confiança total |
| **Pós-Deploy** | `run_tests.py` | - | Confirmação final |

### Comandos Rápidos

```bash
# Setup
.\.venv\Scripts\Activate.ps1 && cd tests\api

# Ciclo de Desenvolvimento Rápido
python diagnose_api.py                                    # Verificação rápida
python -m pytest test_endpoints.py::TestElevatorEndpoint # Validação específica

# Validação Completa
python run_tests.py                                       # Suite completa

# Foco em Endpoint Específico
python -m pytest test_endpoints.py::TestPersonaEndpoint -v
python -m pytest test_endpoints.py::TestCORSHeaders -v
```

## 📁 Estrutura

```
tests/api/
├── __init__.py              # Inicialização do package
├── requirements.txt         # Dependências Python
├── pytest.ini             # Configuração do pytest
├── run_tests.py           # Script principal de execução
├── config.py              # Configurações e payloads de teste
├── client.py              # Cliente HTTP avançado
├── utils.py               # Utilitários e helpers
├── test_endpoints.py      # Testes funcionais dos endpoints
├── test_performance.py    # Testes de performance e carga
└── reports/               # Relatórios gerados
```

## 🛠️ Instalação

```bash
# Navegar para o diretório de testes
cd tests/api

# Instalar dependências
python run_tests.py --install-deps
```

## 🧪 Execução de Testes

### Comandos Básicos

```bash
# Executar todos os testes
python run_tests.py all

# Testes funcionais apenas
python run_tests.py endpoints

# Testes de performance
python run_tests.py performance

# Testes rápidos (smoke tests)
python run_tests.py smoke

# Testes rápidos (sem load/performance)
python run_tests.py quick
```

### Opções Avançadas

```bash
# Verbose output
python run_tests.py all -v

# Sem gerar relatórios
python run_tests.py endpoints --no-report

# Mostrar informações sobre os testes
python run_tests.py --info
```

### Pytest Direto

```bash
# Usar pytest diretamente
pytest test_endpoints.py -v

# Executar testes específicos
pytest test_endpoints.py::TestHealthEndpoint::test_health_check_success -v

# Executar apenas testes rápidos
pytest -m "not slow and not load" -v

# Gerar relatório HTML
pytest --html=reports/report.html --self-contained-html
```

## 📊 Tipos de Teste

### 1. Testes Funcionais (`test_endpoints.py`)

- **Health Check**: Verificação básica do sistema
- **Director**: Criação de missões e orquestração
- **Persona**: Mensagens de usuário e conversas
- **Elevator**: Controle de elevadores
- **PSIM**: Operações de busca e autenticação
- **Coordinator**: Status de missões
- **CORS**: Validação de headers CORS
- **Error Handling**: Tratamento de erros

### 2. Testes de Performance (`test_performance.py`)

- **Response Time**: Tempo de resposta individual
- **Concurrent Requests**: Requisições simultâneas
- **Sustained Load**: Carga sustentada
- **Stress Testing**: Cenários de stress
- **Boundary Conditions**: Condições limite

## 🎯 Exemplos de Uso

### Teste Simples com Cliente

```python
from tests.api import client, config

# Fazer uma requisição
response, data = client.get("/health")
print(f"Status: {response.status_code}")
print(f"Data: {data}")

# Mostrar resumo
client.print_summary()
```

### Teste Personalizado

```python
import pytest
from tests.api import client, TestPayloads

def test_custom_persona():
    payload = TestPayloads.persona_message(
        user_id="custom-user",
        message="Custom test message"
    )
    
    response, data = client.post("/persona", json=payload)
    assert response.status_code == 200
    assert "session_id" in data
```

### Monitoramento de Endpoints

```python
from tests.api import EndpointMonitor

monitor = EndpointMonitor("https://api.example.com")

endpoints = [
    {"endpoint": "/health", "method": "GET"},
    {"endpoint": "/persona", "method": "POST", "payload": {"user_id": "test", "message": "test"}}
]

results = monitor.monitor_all_endpoints(endpoints)
monitor.print_health_report(results)
```

## 📈 Relatórios

### Relatório HTML
- Interface visual com gráficos
- Detalhes de cada teste
- Métricas de performance
- Screenshots de falhas

### Relatório JSON
- Dados estruturados para análise programática
- Métricas detalhadas
- Histórico de requisições
- Integração com ferramentas de CI/CD

### Console Output
- Feedback em tempo real
- Cores e emojis para clareza
- Barras de progresso
- Resumos automáticos

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# URL base da API
export API_BASE_URL="https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com"

# Timeout das requisições (segundos)
export API_TIMEOUT=30

# Número de tentativas em caso de falha
export API_RETRY_COUNT=3

# Ambiente de teste
export ENVIRONMENT=dev

# ID de usuário para testes
export TEST_USER_ID=api-test-user
```

### Configuração no Código

```python
from tests.api.config import APIConfig

# Configuração customizada
config = APIConfig(
    base_url="https://custom-api.example.com",
    timeout=60,
    retry_count=5
)
```

## 🚨 Resolução de Problemas

### Testes Falhando

1. **Verificar conectividade**:
   ```bash
   curl -X GET "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/health"
   ```

2. **Verificar logs**:
   - Logs aparecem no console durante execução
   - Verificar relatórios HTML/JSON para detalhes

3. **Executar teste individual**:
   ```bash
   pytest test_endpoints.py::TestHealthEndpoint::test_health_check_success -v -s
   ```

### Performance Issues

1. **Executar apenas testes de performance**:
   ```bash
   python run_tests.py performance
   ```

2. **Verificar métricas no relatório**:
   - Tempo médio de resposta
   - Percentis de latência
   - Taxa de sucesso

### Problemas de Dependências

```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall

# Atualizar pip
python -m pip install --upgrade pip
```

## 🔄 Integração CI/CD

### GitHub Actions

```yaml
- name: Run API Tests
  run: |
    cd tests/api
    python run_tests.py quick --no-report
    
- name: Upload Test Reports
  uses: actions/upload-artifact@v3
  with:
    name: api-test-reports
    path: tests/api/reports/
```

### Azure DevOps

```yaml
- script: |
    cd tests/api
    python run_tests.py all
  displayName: 'Run API Tests'
  
- task: PublishTestResults@2
  inputs:
    testResultsFiles: 'tests/api/reports/*.xml'
```

## 📚 Referências

- [pytest Documentation](https://docs.pytest.org/)
- [requests Documentation](https://docs.python-requests.org/)
- [rich Documentation](https://rich.readthedocs.io/)
- [BuildingOS API Documentation](../../docs/02-architecture/02-api-contract.md)

# Comunicação Chat ↔ Barramento SNS - Nova Arquitetura

## Visão Geral do Fluxo

A comunicação entre o chat frontend e o barramento SNS segue uma arquitetura event-driven com tópicos padronizados e processamento distribuído.

## 🔄 Fluxo Completo de Comunicação

### 1. **Frontend → API Gateway → Persona Agent**

```
Chat Interface
    ↓ HTTP POST
API Gateway (/persona)
    ↓ Lambda Invoke
Persona Agent (Lambda)
```

**Frontend Request:**
```javascript
// Envio da mensagem do usuário
const requestBody = {
    user_id: "web-user-1728312345-abc123def",
    message: "Chame o elevador para o andar 5",
    session_id: "session-uuid-4567" // opcional
};

fetch('https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/persona', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody)
});
```

**Persona Agent Response:**
```javascript
// Resposta imediata (202 Accepted)
{
    "statusCode": 202,
    "session_id": "session-uuid-4567",
    "message": "Sua solicitação está sendo processada...",
    "architecture": "NEW"
}
```

### 2. **Persona Agent → SNS Topic (Intenção)**

```python
# Persona Agent publica intenção no SNS
intention_manifest = {
    "session_id": "session-uuid-4567",
    "user_id": "web-user-1728312345-abc123def",
    "message": "Chame o elevador para o andar 5",
    "timestamp": 1728312345,
    "source": "persona"
}

sns.publish(
    TopicArn=PERSONA_INTENTION_TOPIC_ARN,  # bos-persona-intention-topic-dev
    Message=json.dumps(intention_manifest),
    MessageStructure="string"
)
```

### 3. **SNS → Director Agent (Processamento)**

```
bos-persona-intention-topic-dev
    ↓ SNS Event
Director Agent (Lambda)
    ↓ Claude AI Processing
Mission Planning
```

**Director Agent Processing:**
```python
# Director Agent recebe a intenção via SNS
def handler(event, context):
    for record in event["Records"]:
        message = json.loads(record["Sns"]["Message"])
        
        # Análise da intenção com Claude AI
        bedrock_response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({
                "messages": [{"role": "user", "content": f"Analyze: {message['message']}"}],
                "max_tokens": 1000
            })
        )
        
        # Criação da missão
        mission = create_mission_from_intention(message)
        
        # Publicação para agente especialista
        sns.publish(
            TopicArn=DIRECTOR_MISSION_TOPIC_ARN,  # bos-director-mission-topic-dev
            Message=json.dumps(mission)
        )
```

### 4. **Director → Specialist Agent (Execução)**

```
bos-director-mission-topic-dev
    ↓ SNS Event
Elevator Agent (Lambda)
    ↓ API Call
Building Systems
```

**Elevator Agent Execution:**
```python
# Elevator Agent executa a tarefa
def call_elevator_to_floor(floor):
    # API call para sistema de elevadores
    response = requests.post(
        "https://elevators-api.building.local/call",
        json={"floor": floor, "building_id": "main"}
    )
    
    return {
        "status": "success" if response.ok else "error",
        "message": f"Elevador chamado para andar {floor}",
        "elevator_id": response.json().get("elevator_id")
    }
```

### 5. **Specialist Agent → SNS (Resultado)**

```python
# Agente publica resultado
mission_result = {
    "mission_id": "mission-uuid-7890",
    "user_id": "web-user-1728312345-abc123def",
    "status": "completed",
    "tasks": [
        {
            "task_id": "task-uuid-1234",
            "action": "call_elevator",
            "status": "completed",
            "result": {
                "status": "success",
                "message": "✅ Elevador chamado para andar 5 - ETA 30 segundos",
                "elevator_id": "ELV-001"
            }
        }
    ]
}

sns.publish(
    TopicArn=COORDINATOR_MISSION_RESULT_TOPIC_ARN,  # bos-coordinator-mission-result-topic-dev
    Message=json.dumps(mission_result)
)
```

### 6. **SNS → Persona Agent (Resultado Final)**

```python
# Persona Agent recebe resultado via SNS
def handle_mission_result(message):
    mission_result = json.loads(message)
    
    # Salva resposta no DynamoDB
    conversation_item = {
        "ConversationId": str(uuid.uuid4()),
        "UserId": mission_result["user_id"],
        "SessionId": session_id,
        "Role": "assistant",
        "Message": "✅ Elevador chamado para andar 5 - ETA 30 segundos",
        "Timestamp": int(time.time()),
        "ExpiresAt": expires_at
    }
    
    table.put_item(Item=conversation_item)
```

### 7. **Frontend Polling → Resposta**

```javascript
// Frontend faz polling para buscar novas mensagens
async function pollForNewMessages() {
    const url = `${API_ENDPOINT}/persona?user_id=${USER_ID}&session=${currentSession}`;
    const response = await fetch(url, { method: 'GET' });
    
    if (response.ok) {
        const data = await response.json();
        
        // Processa novas mensagens
        if (data.messages && data.messages.length > lastMessageCount) {
            const newMessages = data.messages.slice(lastMessageCount);
            
            newMessages.forEach(msg => {
                if (msg.Role === 'assistant') {
                    // Exibe resposta do sistema
                    addMessage(msg.Message, 'assistant', msg.Timestamp);
                    
                    // Notificação do browser se for resultado importante
                    if (msg.Message.includes('✅') || msg.Message.includes('Elevador')) {
                        showBrowserNotification(msg.Message);
                    }
                }
            });
        }
    }
}

// Polling a cada 2 segundos
setInterval(pollForNewMessages, 2000);
```

## 🏗️ Arquitetura dos Tópicos SNS

### Tópicos Padronizados (Pattern: `bos-{agent}-{action}-topic-{env}`)

```
1. bos-persona-intention-topic-dev
   ├── Subscriber: Director Agent
   └── Purpose: Intenções dos usuários
   
2. bos-director-mission-topic-dev
   ├── Subscribers: Elevator Agent, Door Agent, etc.
   └── Purpose: Missões para agentes especialistas
   
3. bos-coordinator-mission-result-topic-dev
   ├── Subscriber: Persona Agent
   └── Purpose: Resultados das missões
   
4. bos-director-response-topic-dev
   ├── Subscriber: Persona Agent
   └── Purpose: Respostas elaboradas do Director
```

## 💾 Persistência de Dados

### DynamoDB - Conversation Table

```json
{
    "ConversationId": "conv-uuid-1234",
    "UserId": "web-user-1728312345-abc123def",
    "SessionId": "session-uuid-4567",
    "Role": "user|assistant",
    "Message": "Chame o elevador para o andar 5",
    "Timestamp": 1728312345,
    "ExpiresAt": 1728398745
}
```

### DynamoDB - Mission State Table

```json
{
    "MissionId": "mission-uuid-7890",
    "UserId": "web-user-1728312345-abc123def",
    "SessionId": "session-uuid-4567",
    "Status": "completed",
    "CreatedAt": 1728312345,
    "UpdatedAt": 1728312350,
    "Tasks": [...]
}
```

## ⚡ Fluxo de Tempo Real

```
T+0s:  User digita "Chame elevador"
T+0.1s: Frontend → API Gateway → Persona Agent
T+0.2s: Persona Agent → SNS (intention)
T+0.3s: SNS → Director Agent
T+0.5s: Director Agent → Claude AI (análise)
T+1s:   Director Agent → SNS (mission)
T+1.1s: SNS → Elevator Agent
T+1.5s: Elevator Agent → Building API
T+2s:   Elevator Agent → SNS (result)
T+2.1s: SNS → Persona Agent
T+2.2s: Persona Agent → DynamoDB (save)
T+4s:   Frontend polling → Nova mensagem!
T+4.1s: UI atualizada com "✅ Elevador chamado"
```

## 🔄 Polling Inteligente

### Estratégia de Polling

```javascript
// Polling otimizado com backoff
const POLLING_INTERVALS = {
    ACTIVE: 2000,      // 2s quando ativo
    BACKGROUND: 5000,  // 5s quando em background
    OFFLINE: 30000     // 30s quando offline
};

// Ajuste dinâmico baseado na atividade
function adjustPollingRate() {
    if (document.hidden) {
        return POLLING_INTERVALS.BACKGROUND;
    } else if (isUserActive) {
        return POLLING_INTERVALS.ACTIVE;
    } else {
        return POLLING_INTERVALS.OFFLINE;
    }
}
```

## 🛡️ Tratamento de Erros

### Retry Logic

```javascript
// Retry com exponential backoff
async function sendMessageWithRetry(message, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await sendMessageToPersona(message);
        } catch (error) {
            if (attempt === maxRetries) throw error;
            
            const delay = Math.pow(2, attempt) * 1000; // 2s, 4s, 8s
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
}
```

## 📊 Monitoramento

### Métricas Importantes

```
1. Latência E2E: Tempo total do frontend até resposta final
2. Taxa de Polling: Frequência de polls vs. novas mensagens
3. Taxa de Erro: Falhas na comunicação SNS
4. Throughput: Mensagens por segundo no barramento
5. Utilização DynamoDB: Read/Write capacity units
```

## 🔧 Debugging

### Logs de Debug

```javascript
// Frontend debugging
if (window.location.search.includes('debug=1')) {
    console.log('🔧 Debug Mode Enabled');
    console.log('User ID:', USER_ID);
    console.log('Session ID:', currentSession);
    console.log('Last Poll Result:', lastPollResult);
}
```

### CloudWatch Logs

```
Persona Agent: /aws/lambda/buildingos-agent-persona-dev
Director Agent: /aws/lambda/buildingos-agent-director-dev
Elevator Agent: /aws/lambda/buildingos-agent-elevator-dev
```

## ✅ Vantagens da Nova Arquitetura

1. **Desacoplamento**: Frontend não conhece agentes específicos
2. **Escalabilidade**: SNS distribui carga automaticamente
3. **Resiliência**: Retry automático e dead letter queues
4. **Observabilidade**: Logs centralizados e métricas
5. **Flexibilidade**: Fácil adição de novos agentes
6. **Performance**: Polling otimizado e cache inteligente

Esta arquitetura garante comunicação robusta, escalável e em tempo real entre o chat e todos os sistemas do BuildingOS! 🏗️🚀

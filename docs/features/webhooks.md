# Sistema de Webhooks

## Visão Geral

O sistema de webhooks permite que aplicações externas recebam notificações em tempo real sobre eventos na plataforma.

## Eventos Suportados

1. **Leads**
   - `lead.created`
   - `lead.updated`
   - `lead.converted`

2. **Deals**
   - `deal.created`
   - `deal.updated`
   - `deal.stage_changed`
   - `deal.won`
   - `deal.lost`

3. **Proposals**
   - `proposal.created`
   - `proposal.sent`
   - `proposal.accepted`
   - `proposal.rejected`

4. **Integrations**
   - `integration.connected`
   - `integration.sync_completed`
   - `integration.error`

## Configuração

### Backend

1. Instalar dependências:
```bash
pip install httpx cryptography
```

2. Configurar webhook:
```python
from src.api.services.webhook_service import WebhookService

webhook_service = WebhookService(db)
webhook = webhook_service.create_webhook(
    WebhookCreate(
        name="Meu Webhook",
        url="https://api.meuapp.com/webhook",
        events=["deal.created", "deal.won"],
        headers={
            "X-Custom-Header": "valor"
        },
        secret_key="chave-secreta"
    ),
    user_id=1
)
```

### Frontend

```typescript
// Criar webhook
const webhook = await apiClient.post('/api/webhooks', {
    name: "Meu Webhook",
    url: "https://api.meuapp.com/webhook",
    events: ["deal.created", "deal.won"],
    headers: {
        "X-Custom-Header": "valor"
    },
    secret_key: "chave-secreta"
});
```

## Formato das Notificações

### Headers
```
Content-Type: application/json
User-Agent: Claude-MCP-Webhook/1.0
X-Webhook-ID: 123
X-Delivery-ID: 456
X-Event-Type: deal.created
X-Signature: assinatura-hmac
```

### Payload
```json
{
    "event_type": "deal.created",
    "created_at": "2025-02-20T09:34:00Z",
    "data": {
        "id": 1,
        "title": "Novo Negócio",
        "value": 1000.00,
        "status": "new"
    }
}
```

## Segurança

### Assinatura HMAC
```python
# Gerar assinatura
import hmac
import hashlib
import json

def generate_signature(secret_key: str, payload: dict) -> str:
    payload_bytes = json.dumps(payload, sort_keys=True).encode()
    return hmac.new(
        secret_key.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
```

### Verificação
```python
# No receptor
received_signature = request.headers.get("X-Signature")
computed_signature = generate_signature(SECRET_KEY, request.json())

if not hmac.compare_digest(received_signature, computed_signature):
    raise ValueError("Invalid signature")
```

## Retry Logic

1. **Configuração**
```python
webhook = WebhookCreate(
    name="Meu Webhook",
    url="https://api.example.com/webhook",
    retry_count=3  # Tentativas máximas
)
```

2. **Backoff Exponencial**
```python
attempt = 1
while attempt <= max_attempts:
    try:
        # Tentar entrega
        if success:
            break
    except:
        # Esperar antes da próxima tentativa
        await asyncio.sleep(2 ** attempt)
    attempt += 1
```

## Monitoramento

### Logs de Entrega
```python
# Obter histórico
deliveries = webhook_service.get_deliveries(
    webhook_id=1,
    limit=100
)

for delivery in deliveries:
    print(f"""
    ID: {delivery.id}
    Status: {delivery.status}
    Tentativas: {delivery.attempt_count}
    Erro: {delivery.error_message}
    """)
```

### Métricas
- Taxa de sucesso
- Tempo de resposta
- Falhas por tipo
- Retentativas por webhook

### Alertas
- Falhas consecutivas
- Alta latência
- Erros de certificado
- Expiração de segredos

## Boas Práticas

1. **Implementação**
   - Use HTTPS sempre
   - Valide assinaturas
   - Processe assincronamente
   - Responda rapidamente

2. **Recebimento**
   - Confirme rapidamente (2xx)
   - Valide payload
   - Processe em background
   - Trate idempotência

3. **Retry**
   - Backoff exponencial
   - Jitter aleatório
   - Limite de tentativas
   - Log de falhas

4. **Monitoramento**
   - Alerte falhas
   - Monitore performance
   - Audite acessos
   - Rotacione segredos

## Exemplos

### Trigger de Evento
```python
# Disparar evento
event = WebhookEvent(
    event_type="deal.created",
    payload={
        "id": 1,
        "title": "Novo Negócio",
        "value": 1000.00
    }
)

deliveries = await webhook_service.trigger_event(event)
```

### Retry Manual
```python
# Retentar entrega falha
delivery = await webhook_service.retry_delivery(delivery_id=1)
if delivery and delivery.is_success:
    print("Entrega realizada com sucesso")
```

### Chamada HTTP
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        webhook.url,
        json=payload,
        headers={
            "X-Signature": signature,
            "X-Event-Type": event_type
        }
    )
    
    success = 200 <= response.status_code < 300
```

## Troubleshooting

1. **Falhas Comuns**
   - Timeout de conexão
   - DNS não resolve
   - Certificado inválido
   - Payload inválido

2. **Debugando**
   - Verifique logs
   - Valide payload
   - Teste signature
   - Cheque DNS

3. **Prevenção**
   - Monitore ativamente
   - Valide endpoints
   - Rotacione chaves
   - Mantenha logs
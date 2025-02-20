# Integrações Externas

## Visão Geral

O sistema de integrações externas permite conectar a plataforma com diversos serviços:

- CRM (HubSpot, Pipedrive)
- Pagamentos (Stripe)
- Email (SendGrid)
- Calendário (Google Calendar)
- Armazenamento (AWS S3)

## Provedores Suportados

### CRM
- **HubSpot**
  - Contatos
  - Negócios
  - Tarefas
- **Pipedrive**
  - Pessoas
  - Negócios
  - Atividades

### Pagamentos
- **Stripe**
  - Pagamentos
  - Assinaturas
  - Reembolsos

### Email
- **SendGrid**
  - Envio
  - Templates
  - Analytics

### Calendário
- **Google Calendar**
  - Eventos
  - Participantes
  - Lembretes

### Armazenamento
- **AWS S3**
  - Upload
  - Download
  - Exclusão

## Configuração

### Backend

1. Instalar dependências:
```bash
pip install httpx python-jose passlib bcrypt
```

2. Configurar provedores em `src/api/integrations/providers.py`:
```python
PROVIDERS = {
    "hubspot": IntegrationProvider(
        id="hubspot",
        name="HubSpot",
        type="crm",
        # ...configurações...
    )
}
```

3. Implementar cliente em `src/api/integrations/clients/`:
```python
class HubSpotClient(CRMClient):
    async def initialize(self) -> bool:
        # Inicialização
        pass
```

### Frontend

1. Adicionar configuração:
```typescript
const integration = await apiClient.post('/api/integrations', {
    name: "MeuCRM",
    type: "crm",
    provider: "hubspot",
    config: {
        sync_contacts: true,
        sync_deals: true
    },
    credentials: {
        client_id: "xxx",
        client_secret: "xxx"
    }
});
```

## Uso

### Criar Integração

```python
from src.api.services.integration_service import IntegrationService

integration_service = IntegrationService(db)
integration = await integration_service.create_integration(
    IntegrationCreate(
        name="MeuCRM",
        provider="hubspot",
        config={
            "sync_contacts": True,
            "sync_deals": True
        },
        credentials={
            "client_id": "xxx",
            "client_secret": "xxx"
        }
    ),
    user_id=1
)
```

### Sincronizar Dados

```python
# Sincronização manual
sync_log = await integration_service.sync_integration(integration.id)

# Verificar status
print(f"Status: {sync_log.status}")
print(f"Itens processados: {sync_log.items_processed}")
print(f"Sucessos: {sync_log.items_succeeded}")
print(f"Falhas: {sync_log.items_failed}")
```

### Usar no Frontend

```typescript
import { useApi } from '@/hooks/useApi';
import { integrationService } from '@/api/services/integrations';

function IntegrationsPage() {
    const { data: integrations } = useApi(integrationService.getIntegrations);
    
    return (
        <div>
            {integrations?.map(integration => (
                <div key={integration.id}>
                    <h3>{integration.name}</h3>
                    <p>Status: {integration.status}</p>
                </div>
            ))}
        </div>
    );
}
```

## Autenticação

### OAuth 2.0
1. Redirecionar para autorização
2. Receber código
3. Trocar por token
4. Armazenar refresh token

### API Key
1. Solicitar chave do provedor
2. Configurar na integração
3. Usar em requisições

### Basic Auth
1. Configurar usuário/senha
2. Codificar em Base64
3. Incluir no header

## Sincronização

### Modos
1. **Manual**: Via API
2. **Agendado**: Cron jobs
3. **Webhook**: Eventos em tempo real

### Estratégias
1. Sincronização completa
2. Sincronização incremental
3. Sincronização bidirecional

## Segurança

1. **Credenciais**
   - Criptografia em repouso
   - Rotação de chaves
   - Gerenciamento de segredos

2. **Auditoria**
   - Log de ações
   - Histórico de sincronização
   - Monitoramento

3. **Permissões**
   - Controle de acesso
   - Escopos OAuth
   - Políticas de IP

## Tratamento de Erros

1. **Retry Logic**
   - Tentativas exponenciais
   - Jitter aleatório
   - Máximo de retentativas

2. **Circuit Breaker**
   - Detecção de falhas
   - Estado meio-aberto
   - Reset automático

3. **Fallback**
   - Cache local
   - Modo offline
   - Dados padrão

## Monitoramento

1. **Métricas**
   - Taxa de sucesso
   - Tempo de resposta
   - Uso de recursos

2. **Alertas**
   - Falhas críticas
   - Limites de uso
   - Performance degradada

3. **Dashboards**
   - Status em tempo real
   - Histórico de eventos
   - Tendências

## Boas Práticas

1. **Desenvolvimento**
   - Interfaces bem definidas
   - Código idempotente
   - Testes completos

2. **Operação**
   - Logs detalhados
   - Monitoramento proativo
   - Backup regular

3. **Manutenção**
   - Atualizações regulares
   - Documentação atualizada
   - Revisões de segurança
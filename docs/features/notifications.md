# Sistema de Notificações

## Visão Geral

O sistema de notificações suporta três tipos de notificações:
- In-app (notificações no aplicativo)
- Email
- Push

## Configuração

1. Backend Setup:
```python
# .env
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USER=user@example.com
EMAIL_PASSWORD=password

PUSH_SERVICE_KEY=your_key
```

2. Frontend Setup:
```bash
# Instale as dependências necessárias
npm install @/components/ui/popover lucide-react
```

## Uso

### Backend

1. Enviar Notificação:
```python
from src.api.services.notification_service import NotificationService
from src.api.models.notification import NotificationCreate

notification_service = NotificationService(db, background_tasks)
await notification_service.create_notification(
    NotificationCreate(
        user_id=user.id,
        type="in_app",  # "email" ou "push"
        title="Nova proposta",
        content="Uma nova proposta foi criada"
    )
)
```

2. Consultar Notificações:
```python
# Obter notificações não lidas
notifications = notification_service.get_user_notifications(
    user_id=user.id,
    unread_only=True
)
```

3. Marcar como Lida:
```python
notification = notification_service.mark_as_read(
    notification_id=1,
    user_id=user.id
)
```

### Frontend

1. Adicionar o Componente de Notificação:
```tsx
// layout.tsx
import { NotificationBell } from '@/components/Notifications';

export default function Layout() {
  return (
    <div>
      <header>
        <NotificationBell />
      </header>
      {/* resto do layout */}
    </div>
  );
}
```

2. Usar o Hook de Notificações:
```tsx
import { useNotifications } from '@/hooks/useNotifications';

function MyComponent() {
  const { 
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead 
  } = useNotifications();

  return (
    <div>
      <h2>Notificações ({unreadCount})</h2>
      {/* renderizar notificações */}
    </div>
  );
}
```

## Customização

### Estilos

O componente NotificationBell usa Tailwind CSS e pode ser customizado através das classes:

```tsx
<NotificationBell 
  className="custom-bell-class"
  badgeClassName="custom-badge-class"
/>
```

### Configurações

1. Polling Interval:
```tsx
const { notifications } = useNotifications({
  pollingInterval: 60000, // 1 minuto
});
```

2. Limite de Notificações:
```tsx
const { notifications } = useNotifications({
  limit: 100, // máximo de notificações para carregar
});
```

## Exemplo Completo

```tsx
import { useNotifications } from '@/hooks/useNotifications';
import { NotificationList } from '@/components/Notifications';

function NotificationsPage() {
  const { 
    notifications,
    unreadCount,
    loading,
    error,
    markAllAsRead 
  } = useNotifications();

  if (loading) return <div>Carregando...</div>;
  if (error) return <div>Erro: {error.message}</div>;

  return (
    <div>
      <div className="flex justify-between items-center">
        <h1>Notificações ({unreadCount})</h1>
        <button onClick={markAllAsRead}>
          Marcar todas como lidas
        </button>
      </div>
      <NotificationList />
    </div>
  );
}
```

## Boas Práticas

1. Sempre utilize background tasks para envio de email/push
2. Implemente rate limiting para polling
3. Configure TTL para limpeza automática de notificações antigas
4. Considere websockets para notificações em tempo real
5. Implemente retry logic para envios falhos
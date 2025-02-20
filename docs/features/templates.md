# Sistema de Templates

## Visão Geral

O sistema de templates oferece uma solução flexível para criar, gerenciar e renderizar templates dinâmicos. Suporta:

- Templates para e-mails, documentos e propostas
- Variáveis dinâmicas com validação de tipo
- Versionamento de templates
- Templates padrão por tipo
- Pré-visualização em tempo real

## Tipos de Templates

1. **Email**
   - Suporte a HTML
   - Variáveis personalizadas
   - Templates responsivos

2. **Documento**
   - Formatação rica
   - Seções dinâmicas
   - Dados variáveis

3. **Proposta**
   - Campos calculados
   - Formatação condicional
   - Dados do cliente

## Uso

### Backend

1. Criar Template:
```python
from src.api.services.template_service import TemplateService
from src.api.models.template import TemplateCreate

template = TemplateCreate(
    name="Proposta Padrão",
    type="proposal",
    content="""
    Prezado {{ client.name }},
    
    Segue proposta no valor de R$ {{ value }}.
    
    Atenciosamente,
    {{ user.name }}
    """,
    variables={
        "client.name": {
            "type": "string",
            "required": True
        },
        "value": {
            "type": "number",
            "required": True
        },
        "user.name": {
            "type": "string",
            "required": True
        }
    }
)

template_service = TemplateService(db)
created = template_service.create_template(template, user_id=1)
```

2. Renderizar Template:
```python
variables = {
    "client.name": "João Silva",
    "value": 1000.00,
    "user.name": "Maria Santos"
}

content = template_service.render_template(template, variables)
```

### Frontend

1. Editor de Templates:
```tsx
import { TemplateEditor } from '@/components/Templates';

function TemplatePage() {
  return (
    <TemplateEditor
      onSave={template => {
        console.log('Template salvo:', template);
      }}
    />
  );
}
```

2. Pré-visualização:
```tsx
import { TemplatePreview } from '@/components/Templates';

function PreviewPage({ template }) {
  return (
    <TemplatePreview
      template={template}
      initialVariables={{
        "client.name": "João Silva"
      }}
      onUse={content => {
        console.log('Conteúdo gerado:', content);
      }}
    />
  );
}
```

## Estrutura de Variáveis

Cada variável no template possui um schema que define:

```typescript
interface VariableSchema {
  type: 'string' | 'number' | 'boolean' | 'date';
  required?: boolean;
  default?: any;
  options?: string[];  // Para variáveis com valores predefinidos
  description?: string;
}
```

Exemplo:
```json
{
  "status": {
    "type": "string",
    "required": true,
    "options": ["draft", "sent", "accepted"],
    "default": "draft"
  },
  "value": {
    "type": "number",
    "required": true,
    "default": 0
  }
}
```

## Boas Práticas

1. Nomeação de Variáveis
   - Use nomes descritivos
   - Separe hierarquias com ponto (.)
   - Evite caracteres especiais

2. Estrutura de Templates
   - Divida em seções lógicas
   - Use comentários para documentar
   - Mantenha a formatação consistente

3. Validação
   - Sempre defina tipos para variáveis
   - Valide dados antes de renderizar
   - Trate erros apropriadamente

4. Versionamento
   - Atualize a versão ao modificar
   - Mantenha templates antigos
   - Documente mudanças

## Exemplos

### Template de Email

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; }
    .header { background: #f5f5f5; padding: 20px; }
    .content { padding: 20px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>{{ title }}</h1>
  </div>
  <div class="content">
    <p>Olá {{ recipient.name }},</p>
    
    {% if show_proposal %}
      <p>Sua proposta no valor de R$ {{ proposal.value }} foi {{ status }}.</p>
    {% endif %}
    
    <p>Atenciosamente,<br>{{ sender.name }}</p>
  </div>
</body>
</html>
```

### Template de Proposta

```markdown
# Proposta Comercial

**Cliente:** {{ client.name }}
**Data:** {{ date | date('DD/MM/YYYY') }}
**Validade:** {{ validity_days }} dias

## Escopo

{{ scope }}

## Valores

| Item | Valor |
|------|-------|
{% for item in items %}
| {{ item.name }} | R$ {{ item.value | number('0,0.00') }} |
{% endfor %}

**Total:** R$ {{ total | number('0,0.00') }}

## Condições

- Prazo de entrega: {{ delivery_days }} dias
- Forma de pagamento: {{ payment_terms }}

{% if has_discount %}
**Desconto especial:** {{ discount }}%
{% endif %}
```

## Cache

O sistema implementa cache de templates usando Redis:

```python
CACHE_KEY = f"template:{template_id}:v{version}"
CACHE_TTL = 3600  # 1 hora

# Get from cache
cached = await redis.get(CACHE_KEY)
if cached:
    return json.loads(cached)

# Render and cache
content = template_service.render_template(template, variables)
await redis.setex(CACHE_KEY, CACHE_TTL, json.dumps(content))
```

## Segurança

1. Sanitização
   - Escape HTML em variáveis
   - Valide tipos de dados
   - Previna injeção de código

2. Permissões
   - Controle acesso por usuário
   - Restrinja edição
   - Audite mudanças

3. Validação
   - Verifique dados de entrada
   - Limite tamanho de templates
   - Valide sintaxe antes de salvar
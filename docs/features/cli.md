# CLI Avançada

## Visão Geral

A CLI oferece uma interface de linha de comando completa para gerenciar todos os aspectos da plataforma.

## Instalação

1. **Via pip**:
```bash
pip install claude-mcp-toolkit
```

2. **Via código fonte**:
```bash
git clone https://github.com/Lucasdoreac/claude-mcp-toolkit.git
cd claude-mcp-toolkit
pip install -e .
```

## Configuração

### Variáveis de Ambiente
```bash
# API URL (opcional, padrão: http://localhost:8000)
export MCP_API_URL=http://api.example.com

# Token de autenticação (opcional)
export MCP_TOKEN=seu-token
```

### Login
```bash
# Login interativo
mcp login

# Login com argumentos
mcp login --username admin --password senha123
```

## Comandos

### Templates

1. **Listar templates**:
```bash
# Listar todos
mcp templates list

# Filtrar por tipo
mcp templates list --type email
```

2. **Criar template**:
```bash
# Interativo
mcp templates create "Email de Boas-vindas" \
  --type email \
  --file template.html \
  --variables variables.json

# Editor
mcp templates create "Email de Boas-vindas" --type email
```

3. **Visualizar template**:
```bash
mcp templates show 123
```

4. **Renderizar template**:
```bash
# Saída para arquivo
mcp templates render 123 variables.json -o output.html

# Saída para console
mcp templates render 123 variables.json
```

### Integrações

1. **Listar provedores**:
```bash
# Todos provedores
mcp integrations providers

# Por tipo
mcp integrations providers --type crm
```

2. **Criar integração**:
```bash
mcp integrations create "Meu CRM" hubspot \
  --config config.json \
  --credentials credentials.json
```

3. **Sincronizar**:
```bash
# Sync manual
mcp integrations sync 123

# Ver logs
mcp integrations logs 123 --limit 50
```

### Webhooks

1. **Gerenciar webhooks**:
```bash
# Criar
mcp webhooks create "Notificações" https://api.example.com/webhook \
  --events "deal.created,deal.won" \
  --secret "chave-secreta"

# Listar
mcp webhooks list

# Ver entregas
mcp webhooks deliveries 123 --limit 50
```

2. **Testar webhook**:
```bash
# Trigger manual
mcp webhooks trigger 123 deal.created payload.json

# Retry entrega
mcp webhooks retry 456
```

## Exemplos

### Pipeline Completo

```bash
# Criar template
mcp templates create "Proposta" --type proposal --file proposal.md

# Criar integração CRM
mcp integrations create "MeuCRM" hubspot \
  --config crm-config.json \
  --credentials crm-auth.json

# Criar webhook para notificações
mcp webhooks create "Notificações Slack" https://hooks.slack.com/... \
  --events "deal.won,proposal.accepted" \
  --secret "webhook-secret"

# Sync inicial
mcp integrations sync 123
```

### Automação

```bash
# Script de setup
#!/bin/bash

# Login
mcp login --username $MCP_USER --password $MCP_PASS

# Templates
for template in templates/*.json; do
  name=$(jq -r .name $template)
  type=$(jq -r .type $template)
  mcp templates create "$name" --type $type --file $template
done

# Integrações
for integration in integrations/*.json; do
  name=$(jq -r .name $integration)
  provider=$(jq -r .provider $integration)
  mcp integrations create "$name" $provider \
    --config $integration \
    --credentials secrets/$provider.json
done

# Webhooks
for webhook in webhooks/*.json; do
  mcp webhooks create $(jq -r '.name,.url,.events' $webhook)
done
```

### CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      
      - name: Install MCP CLI
        run: pip install claude-mcp-toolkit

      - name: Configure CLI
        run: |
          echo "MCP_API_URL=${{ secrets.MCP_API_URL }}" >> $GITHUB_ENV
          echo "MCP_TOKEN=${{ secrets.MCP_TOKEN }}" >> $GITHUB_ENV

      - name: Deploy Templates
        run: |
          for template in templates/*.json; do
            mcp templates create $(jq -r '.name,.type' $template) \
              --file $template \
              --variables config/$(basename $template .json).vars.json
          done

      - name: Deploy Integrations
        run: |
          for config in integrations/*.json; do
            provider=$(jq -r .provider $config)
            mcp integrations create $(jq -r .name $config) $provider \
              --config $config \
              --credentials secrets/$provider.json
          done
```

## Configuração Avançada

### Aliases
```bash
# ~/.bashrc ou ~/.zshrc

# Shortcuts
alias mcpt="mcp templates"
alias mcpi="mcp integrations"
alias mcpw="mcp webhooks"

# Comandos comuns
alias mcpl="mcp templates list"
alias mcps="mcp integrations sync"
alias mcpd="mcp webhooks deliveries"
```

### Autocompletion
```bash
# Bash
mcp completion bash > ~/.mcp-completion.bash
echo 'source ~/.mcp-completion.bash' >> ~/.bashrc

# Zsh
mcp completion zsh > ~/.mcp-completion.zsh
echo 'source ~/.mcp-completion.zsh' >> ~/.zshrc
```

### Perfis
```bash
# ~/.mcp/config.yaml
default:
  api_url: http://localhost:8000
  
staging:
  api_url: https://staging-api.example.com
  
production:
  api_url: https://api.example.com

# Usar perfil
mcp --profile production templates list
```

## Troubleshooting

### Exit Codes
- 0: Sucesso
- 1: Erro geral
- 2: Erro de autenticação
- 3: Erro de validação
- 4: Erro de conexão
- 5: Timeout

### Debug Mode
```bash
# Habilitar debug
export MCP_DEBUG=1

# Ver requests HTTP
export MCP_DEBUG_HTTP=1

# Log em arquivo
export MCP_LOG_FILE=/var/log/mcp.log
```

### Cache
```bash
# Limpar cache
mcp cache clear

# Atualizar cache
mcp cache update

# Ver status
mcp cache status
```

## Boas Práticas

1. **Organização**
   - Use um diretório por recurso
   - Nomeie arquivos consistentemente
   - Mantenha templates versionados

2. **Segurança**
   - Use variáveis de ambiente
   - Rotacione tokens
   - Valide inputs

3. **Automação**
   - Crie scripts de setup
   - Automatize deploys
   - Monitore logs
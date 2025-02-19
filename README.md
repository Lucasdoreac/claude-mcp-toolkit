# Guia Prático - Claude MCP Toolkit

Este repositório contém um guia prático para utilização das ferramentas MCP (Model Context Protocol) com Claude Desktop, organizado para facilitar o desenvolvimento e manutenção de projetos.

## 📚 Índice

1. [Gerenciamento de Arquivos](#gerenciamento-de-arquivos)
2. [Integração com GitHub](#integração-com-github)
3. [Gestão de Conhecimento](#gestão-de-conhecimento)
4. [Utilitários](#utilitários)
5. [Workflows Comuns](#workflows-comuns)

## 🗂 Gerenciamento de Arquivos

### Comandos Essenciais
- `create_directory`: Criar diretórios
- `read_file`: Ler conteúdo de arquivos
- `write_file`: Criar/sobrescrever arquivos
- `edit_file`: Editar arquivos existentes
- `move_file`: Mover/renomear arquivos
- `search_files`: Buscar arquivos por padrão

### Práticas Recomendadas
- Sempre verifique diretórios permitidos com `list_allowed_directories`
- Use `directory_tree` para visualizar estrutura completa
- Prefira `read_multiple_files` para análise em lote

## 🐙 Integração com GitHub

### Gestão de Repositórios
- Criar: `create_repository`
- Forkar: `fork_repository`
- Buscar: `search_repositories`

### Gestão de Código
- Criar/atualizar arquivos: `create_or_update_file`
- Push múltiplos arquivos: `push_files`
- Criar branches: `create_branch`

### Issues e PRs
- Criar issues: `create_issue`
- Atualizar issues: `update_issue`
- Criar PRs: `create_pull_request`
- Adicionar comentários: `add_issue_comment`

## 🧠 Gestão de Conhecimento

### Entidades e Relações
- Criar entidades: `create_entities`
- Criar relações: `create_relations`
- Adicionar observações: `add_observations`

### Consultas
- Ler grafo completo: `read_graph`
- Buscar nós: `search_nodes`
- Abrir nós específicos: `open_nodes`

## 🛠 Utilitários

### Análise Sequencial
Use `sequentialthinking` para:
- Decomposição de problemas complexos
- Planejamento com revisão
- Análise adaptativa
- Verificação de hipóteses

### Melhores Práticas
1. Sempre comece com um plano estruturado
2. Use controle de versão para todas as alterações
3. Documente decisões importantes
4. Mantenha um histórico de workflows bem-sucedidos

## 🔄 Workflows Comuns

### Iniciando Novo Projeto
1. Criar repositório
2. Configurar estrutura base
3. Documentar requisitos
4. Estabelecer milestones

### Manutenção de Projeto
1. Revisar issues abertas
2. Atualizar documentação
3. Organizar branches
4. Gerenciar PRs

### Análise de Código
1. Buscar padrões relevantes
2. Documentar findings
3. Propor melhorias
4. Implementar correções

## 📖 Como Usar Este Guia

1. Clone este repositório
2. Consulte a seção relevante para sua necessidade
3. Siga os workflows recomendados
4. Contribua com melhorias e feedback

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:
1. Fork o repositório
2. Crie uma branch para sua feature
3. Envie um PR com suas alterações

## 📝 Licença

MIT License - veja o arquivo LICENSE para detalhes.
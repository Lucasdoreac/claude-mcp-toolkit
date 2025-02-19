# Workflow: Iniciando um Novo Projeto

Este exemplo demonstra como usar as ferramentas MCP para iniciar um novo projeto no GitHub.

## 1. Criar o Repositório

```python
# Criar novo repositório
create_repository(
    name="meu-projeto",
    description="Descrição do projeto",
    private=False,
    autoInit=True
)
```

## 2. Configurar Estrutura Base

```python
# Criar estrutura de diretórios básica
files = [
    {
        "path": "src/README.md",
        "content": "# Código Fonte\n\nContém o código fonte do projeto."
    },
    {
        "path": "docs/README.md",
        "content": "# Documentação\n\nContém a documentação do projeto."
    },
    {
        "path": "tests/README.md",
        "content": "# Testes\n\nContém os testes do projeto."
    }
]

push_files(
    owner="seu-usuario",
    repo="meu-projeto",
    branch="main",
    files=files,
    message="Configurar estrutura inicial do projeto"
)
```

## 3. Criar Issues Iniciais

```python
# Criar milestone para primeira versão
create_issue(
    owner="seu-usuario",
    repo="meu-projeto",
    title="Setup Inicial",
    body="Tarefas iniciais para configuração do projeto",
    labels=["setup", "prioridade-alta"]
)

# Criar issues para principais funcionalidades
create_issue(
    owner="seu-usuario",
    repo="meu-projeto",
    title="Implementar Feature X",
    body="Descrição detalhada da Feature X",
    labels=["feature", "prioridade-media"]
)
```

## 4. Criar Branch de Desenvolvimento

```python
# Criar branch de desenvolvimento
create_branch(
    owner="seu-usuario",
    repo="meu-projeto",
    branch="develop"
)
```

## 5. Configurar Proteções (via PR)

```python
# Criar pull request com configurações
create_pull_request(
    owner="seu-usuario",
    repo="meu-projeto",
    title="Configurar proteções de branch",
    body="Adicionar proteções para branches main e develop",
    head="feature/branch-protection",
    base="main"
)
```

## Dicas

1. Sempre inclua um README.md bem estruturado
2. Configure issues templates quando necessário
3. Estabeleça padrões de commit desde o início
4. Documente decisões importantes
5. Use labels para organizar issues
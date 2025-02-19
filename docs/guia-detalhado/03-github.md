# Integração com GitHub

## 🐙 Recursos do GitHub

### Gestão de Repositórios

1. **Criar Repositório**
   ```python
   def criar_novo_projeto(nome, descricao=None, private=False):
       """
       Cria um novo repositório no GitHub
       """
       return create_repository(
           name=nome,
           description=descricao,
           private=private,
           autoInit=True
       )
   ```

2. **Estrutura Base**
   ```python
   def setup_estrutura_base(owner, repo):
       """
       Configura estrutura inicial do projeto
       """
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
           },
           {
               "path": ".github/workflows/ci.yml",
               "content": """
               name: CI
               on: [push, pull_request]
               jobs:
                 test:
                   runs-on: ubuntu-latest
                   steps:
                     - uses: actions/checkout@v2
                     - name: Set up Python
                       uses: actions/setup-python@v2
                       with:
                         python-version: '3.x'
                     - name: Install dependencies
                       run: |
                         python -m pip install --upgrade pip
                         pip install -r requirements.txt
                     - name: Run tests
                       run: |
                         pytest
               """
           }
       ]
       
       return push_files(
           owner=owner,
           repo=repo,
           branch="main",
           files=files,
           message="Configurar estrutura inicial do projeto"
       )
   ```

### Gestão de Issues

1. **Sistema de Issues**
   ```python
   def gerenciar_issues(owner, repo):
       """
       Sistema completo de gestão de issues
       """
       
       def criar_issue(titulo, corpo, labels=None):
           return create_issue(
               owner=owner,
               repo=repo,
               title=titulo,
               body=corpo,
               labels=labels or []
           )
       
       def atualizar_issue(numero, status=None, comentario=None):
           if status:
               update_issue(
                   owner=owner,
                   repo=repo,
                   issue_number=numero,
                   state=status
               )
           
           if comentario:
               add_issue_comment(
                   owner=owner,
                   repo=repo,
                   issue_number=numero,
                   body=comentario
               )
       
       def listar_issues(estado="open"):
           return list_issues(
               owner=owner,
               repo=repo,
               state=estado
           )
       
       return {
           "criar": criar_issue,
           "atualizar": atualizar_issue,
           "listar": listar_issues
       }
   ```

### Pull Requests

1. **Gestão de PRs**
   ```python
   def workflow_pr(owner, repo, feature_branch, titulo, descricao):
       """
       Workflow completo para PRs
       """
       # Criar branch
       create_branch(
           owner=owner,
           repo=repo,
           branch=feature_branch
       )
       
       # Criar PR
       pr = create_pull_request(
           owner=owner,
           repo=repo,
           title=titulo,
           body=descricao,
           head=feature_branch,
           base="main"
       )
       
       return pr
   ```

2. **Automação de Review**
   ```python
   def setup_review_automation(owner, repo):
       """
       Configura automação para review de PRs
       """
       workflow = """
       name: PR Review Automation
       on:
         pull_request:
           types: [opened, synchronize]
       
       jobs:
         review:
           runs-on: ubuntu-latest
           steps:
             - uses: actions/checkout@v2
             - name: Run linters
               run: |
                 pip install black flake8
                 black --check .
                 flake8 .
             - name: Run tests
               run: |
                 pip install pytest
                 pytest
       """
       
       create_or_update_file(
           owner=owner,
           repo=repo,
           path=".github/workflows/pr-review.yml",
           content=workflow,
           message="Adicionar automação de review de PR"
       )
   ```

### Gerenciamento de Código

1. **Busca de Código**
   ```python
   def buscar_codigo(query, linguagem=None):
       """
       Busca código em repositórios
       """
       q = query
       if linguagem:
           q += f" language:{linguagem}"
           
       return search_code(q=q)
   ```

2. **Análise de Commits**
   ```python
   def analisar_commits(owner, repo, branch="main"):
       """
       Analisa histórico de commits
       """
       commits = list_commits(
           owner=owner,
           repo=repo,
           sha=branch
       )
       
       analise = {
           "total": len(commits),
           "autores": set(),
           "datas": []
       }
       
       for commit in commits:
           analise["autores"].add(commit["commit"]["author"]["name"])
           analise["datas"].append(commit["commit"]["author"]["date"])
           
       return analise
   ```

### Templates e Padrões

1. **Issue Templates**
   ```python
   def setup_issue_templates(owner, repo):
       """
       Configura templates para issues
       """
       templates = {
           "bug_report.md": """
           ---
           name: Bug Report
           about: Create a report to help us improve
           ---
           
           ## Descrição
           
           ## Passos para Reproduzir
           
           ## Comportamento Esperado
           
           ## Screenshots
           
           ## Ambiente
           """,
           
           "feature_request.md": """
           ---
           name: Feature Request
           about: Suggest an idea for this project
           ---
           
           ## Problema Relacionado
           
           ## Solução Proposta
           
           ## Alternativas Consideradas
           
           ## Contexto Adicional
           """
       }
       
       for nome, conteudo in templates.items():
           create_or_update_file(
               owner=owner,
               repo=repo,
               path=f".github/ISSUE_TEMPLATE/{nome}",
               content=conteudo,
               message=f"Adicionar template: {nome}"
           )
   ```

### Workflows Avançados

1. **CI/CD Completo**
   ```python
   def setup_cicd(owner, repo):
       """
       Configura pipeline completo de CI/CD
       """
       workflow = """
       name: CI/CD Pipeline
       
       on:
         push:
           branches: [ main ]
         pull_request:
           branches: [ main ]
       
       jobs:
         test:
           runs-on: ubuntu-latest
           steps:
             - uses: actions/checkout@v2
             - name: Set up Python
               uses: actions/setup-python@v2
             - name: Install dependencies
               run: |
                 python -m pip install --upgrade pip
                 pip install -r requirements.txt
             - name: Run tests
               run: pytest
             - name: Run linters
               run: |
                 pip install black flake8
                 black --check .
                 flake8 .
         
         deploy:
           needs: test
           runs-on: ubuntu-latest
           if: github.ref == 'refs/heads/main'
           steps:
             - uses: actions/checkout@v2
             - name: Deploy
               run: |
                 echo "Deploying..."
       """
       
       create_or_update_file(
           owner=owner,
           repo=repo,
           path=".github/workflows/cicd.yml",
           content=workflow,
           message="Configurar pipeline CI/CD"
       )
   ```

### Exemplos de Uso

1. **Criar Novo Projeto**
   ```python
   # Criar repositório
   repo = criar_novo_projeto("meu-projeto", "Descrição do projeto")
   
   # Configurar estrutura
   setup_estrutura_base(owner="seu-usuario", repo="meu-projeto")
   
   # Configurar templates
   setup_issue_templates(owner="seu-usuario", repo="meu-projeto")
   
   # Configurar CI/CD
   setup_cicd(owner="seu-usuario", repo="meu-projeto")
   ```

2. **Gestão de Issues**
   ```python
   # Inicializar gestor
   issues = gerenciar_issues("seu-usuario", "meu-projeto")
   
   # Criar issue
   nova_issue = issues["criar"](
       "Bug: Login não funciona",
       "O sistema de login está retornando erro 500",
       ["bug", "high-priority"]
   )
   
   # Atualizar status
   issues["atualizar"](
       nova_issue["number"],
       status="closed",
       comentario="Corrigido na versão 1.0.1"
   )
   ```

3. **Criar PR**
   ```python
   # Criar PR para nova feature
   pr = workflow_pr(
       owner="seu-usuario",
       repo="meu-projeto",
       feature_branch="feature/novo-login",
       titulo="Implementar novo sistema de login",
       descricao="- Adiciona autenticação JWT\n- Melhora segurança\n- Adiciona testes"
   )
   ```

### Boas Práticas

1. **Organização**
   - Use branches para features
   - Mantenha commits organizados
   - Documente mudanças

2. **Segurança**
   - Proteja branches principais
   - Configure revisões obrigatórias
   - Use secrets para dados sensíveis

3. **Automação**
   - Implemente CI/CD
   - Use actions para tarefas repetitivas
   - Automatize revisões de código

### Recursos Adicionais

- [GitHub Actions](https://docs.github.com/actions)
- [GitHub API](https://docs.github.com/rest)
- [GitHub CLI](https://cli.github.com)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
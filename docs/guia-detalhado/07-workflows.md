# Workflows Completos

## 🔄 Fluxos de Trabalho Integrados

### Setup Inicial de Projeto

1. **Inicializador de Projeto**
   ```python
   class ProjectInitializer:
       """
       Sistema completo para inicialização de projetos
       """
       def __init__(self, owner, name, description=None):
           self.owner = owner
           self.name = name
           self.description = description
           self.repo = None
   
       def initialize(self):
           """
           Inicializa projeto completo
           """
           try:
               # 1. Criar repositório
               self.repo = create_repository(
                   name=self.name,
                   description=self.description,
                   autoInit=True
               )
   
               # 2. Configurar estrutura base
               self._setup_structure()
   
               # 3. Configurar CI/CD
               self._setup_cicd()
   
               # 4. Configurar documentação
               self._setup_docs()
   
               # 5. Criar issues iniciais
               self._create_initial_issues()
   
               return True
           except Exception as e:
               print(f"Erro na inicialização: {str(e)}")
               return False
   
       def _setup_structure(self):
           """
           Configura estrutura de diretórios e arquivos base
           """
           files = [
               {
                   "path": "src/README.md",
                   "content": "# Código Fonte\n\nContém o código fonte do projeto."
               },
               {
                   "path": "tests/README.md",
                   "content": "# Testes\n\nContém os testes do projeto."
               },
               {
                   "path": "docs/README.md",
                   "content": "# Documentação\n\nContém a documentação do projeto."
               },
               {
                   "path": "requirements.txt",
                   "content": "# Dependências do projeto\n\npandas\nnumpy\nrequests\npython-dotenv"
               },
               {
                   "path": ".env.example",
                   "content": """
                   # Exemplo de configuração
                   API_KEY=sua_chave_aqui
                   DATABASE_URL=url_do_banco
                   """
               },
               {
                   "path": ".gitignore",
                   "content": """
                   # Python
                   __pycache__/
                   *.py[cod]
                   *$py.class
                   .env
                   venv/
                   
                   # IDE
                   .vscode/
                   .idea/
                   
                   # Outros
                   *.log
                   tmp/
                   """
               }
           ]
   
           push_files(
               owner=self.owner,
               repo=self.name,
               branch="main",
               files=files,
               message="Configurar estrutura inicial do projeto"
           )
   
       def _setup_cicd(self):
           """
           Configura pipeline de CI/CD
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
           """
   
           create_or_update_file(
               owner=self.owner,
               repo=self.name,
               path=".github/workflows/cicd.yml",
               content=workflow,
               message="Configurar CI/CD"
           )
   
       def _setup_docs(self):
           """
           Configura documentação inicial
           """
           docs = {
               "docs/api.md": """
               # API Documentation
               
               ## Endpoints
               
               ### GET /api/v1/resource
               
               Descrição do endpoint...
               """,
               "docs/setup.md": """
               # Setup Guide
               
               1. Clone o repositório
               2. Instale dependências
               3. Configure variáveis de ambiente
               4. Execute testes
               """,
               "docs/contributing.md": """
               # Contributing Guide
               
               1. Fork o repositório
               2. Crie uma branch
               3. Faça suas alterações
               4. Envie um PR
               """
           }
   
           for path, content in docs.items():
               create_or_update_file(
                   owner=self.owner,
                   repo=self.name,
                   path=path,
                   content=content,
                   message=f"Adicionar {path}"
               )
   
       def _create_initial_issues(self):
           """
           Cria issues iniciais do projeto
           """
           issues = [
               {
                   "title": "Setup Inicial",
                   "body": "Configurar ambiente inicial do projeto",
                   "labels": ["setup"]
               },
               {
                   "title": "Documentação API",
                   "body": "Criar documentação completa da API",
                   "labels": ["documentation"]
               },
               {
                   "title": "Testes Unitários",
                   "body": "Implementar suite de testes unitários",
                   "labels": ["testing"]
               }
           ]
   
           for issue in issues:
               create_issue(
                   owner=self.owner,
                   repo=self.name,
                   title=issue["title"],
                   body=issue["body"],
                   labels=issue["labels"]
               )
   ```

### Desenvolvimento e Manutenção

1. **Gerenciador de Features**
   ```python
   class FeatureManager:
       """
       Sistema para gestão de desenvolvimento de features
       """
       def __init__(self, owner, repo):
           self.owner = owner
           self.repo = repo
   
       def start_feature(self, name, description):
           """
           Inicia desenvolvimento de nova feature
           """
           # 1. Criar branch
           branch_name = f"feature/{name}"
           create_branch(
               owner=self.owner,
               repo=self.repo,
               branch=branch_name
           )
   
           # 2. Criar issue
           issue = create_issue(
               owner=self.owner,
               repo=self.repo,
               title=f"Feature: {name}",
               body=description,
               labels=["feature"]
           )
   
           # 3. Criar PR draft
           create_pull_request(
               owner=self.owner,
               repo=self.repo,
               title=f"WIP: {name}",
               body=f"Implements #{issue['number']}",
               head=branch_name,
               base="main",
               draft=True
           )
   
       def review_feature(self, pr_number, feedback):
           """
           Processo de review de feature
           """
           add_issue_comment(
               owner=self.owner,
               repo=self.repo,
               issue_number=pr_number,
               body=feedback
           )
   
       def finish_feature(self, pr_number):
           """
           Finaliza desenvolvimento de feature
           """
           # 1. Atualizar PR
           update_pull_request(
               owner=self.owner,
               repo=self.repo,
               pull_number=pr_number,
               state="ready"
           )
   
           # 2. Solicitar review
           request_reviewers(
               owner=self.owner,
               repo=self.repo,
               pull_number=pr_number,
               reviewers=["reviewer1", "reviewer2"]
           )
   ```

2. **Gerenciador de Releases**
   ```python
   class ReleaseManager:
       """
       Sistema para gestão de releases
       """
       def __init__(self, owner, repo):
           self.owner = owner
           self.repo = repo
   
       def prepare_release(self, version, changes):
           """
           Prepara nova release
           """
           # 1. Criar branch de release
           branch_name = f"release/v{version}"
           create_branch(
               owner=self.owner,
               repo=self.repo,
               branch=branch_name
           )
   
           # 2. Atualizar versão
           create_or_update_file(
               owner=self.owner,
               repo=self.repo,
               path="VERSION",
               content=version,
               message=f"Bump version to {version}"
           )
   
           # 3. Atualizar changelog
           self._update_changelog(version, changes)
   
           # 4. Criar PR de release
           create_pull_request(
               owner=self.owner,
               repo=self.repo,
               title=f"Release v{version}",
               body="Prepara nova versão para release",
               head=branch_name,
               base="main"
           )
   
       def _update_changelog(self, version, changes):
           """
           Atualiza CHANGELOG.md
           """
           from datetime import datetime
   
           changelog_entry = f"""
           ## [v{version}] - {datetime.now().strftime('%Y-%m-%d')}
           
           {changes}
           """
   
           try:
               current_changelog = get_file_contents(
                   owner=self.owner,
                   repo=self.repo,
                   path="CHANGELOG.md"
               )
               
               new_content = changelog_entry + "\n" + current_changelog
           except:
               new_content = f"# Changelog\n\n{changelog_entry}"
   
           create_or_update_file(
               owner=self.owner,
               repo=self.repo,
               path="CHANGELOG.md",
               content=new_content,
               message=f"Update changelog for v{version}"
           )
   ```

### Automação e CI/CD

1. **Pipeline Completo**
   ```yaml
   name: Complete CI/CD Pipeline
   
   on:
     push:
       branches: [ main ]
     pull_request:
       branches: [ main ]
   
   jobs:
     validate:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Validate
           run: |
             # Validação de código
             python -m pip install --upgrade pip
             pip install black flake8
             black --check .
             flake8 .
   
     test:
       needs: validate
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Test
           run: |
             # Testes
             pip install pytest pytest-cov
             pytest --cov=src
   
     build:
       needs: test
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Build
           run: |
             # Build do projeto
             pip install build
             python -m build
   
     deploy:
       needs: build
       if: github.ref == 'refs/heads/main'
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Deploy
           run: |
             # Deploy
             echo "Deploying..."
   ```

### Exemplos de Uso

1. **Iniciar Novo Projeto**
   ```python
   # Inicializar projeto
   initializer = ProjectInitializer(
       owner="seu-usuario",
       name="novo-projeto",
       description="Descrição do projeto"
   )
   initializer.initialize()
   ```

2. **Desenvolver Feature**
   ```python
   # Gerenciar feature
   feature_manager = FeatureManager("seu-usuario", "seu-repo")
   
   # Iniciar feature
   feature_manager.start_feature(
       "nova-funcionalidade",
       "Implementa nova funcionalidade X"
   )
   
   # Review
   feature_manager.review_feature(
       pr_number=123,
       feedback="Sugestões de melhorias..."
   )
   
   # Finalizar
   feature_manager.finish_feature(pr_number=123)
   ```

3. **Preparar Release**
   ```python
   # Gerenciar release
   release_manager = ReleaseManager("seu-usuario", "seu-repo")
   
   # Preparar nova versão
   release_manager.prepare_release(
       version="1.0.0",
       changes="""
       ### Added
       - Nova funcionalidade X
       - Suporte para Y
       
       ### Fixed
       - Correção de bug Z
       """
   )
   ```

### Boas Práticas

1. **Organização**
   - Use branches para features
   - Mantenha commits organizados
   - Siga convenções de código
   - Documente mudanças

2. **Qualidade**
   - Execute testes antes de commits
   - Faça code review
   - Use linters e formatadores
   - Mantenha cobertura de testes

3. **Colaboração**
   - Comunique mudanças
   - Use issues para tarefas
   - Documente decisões
   - Mantenha changelog atualizado

### Recursos Adicionais

- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Actions](https://docs.github.com/actions)
- [Python Package Guide](https://packaging.python.org/)
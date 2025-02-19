# Configuração do Ambiente

## 🛠 Setup Inicial

### Requisitos do Sistema

1. **Software Necessário**
   ```bash
   # Python 3.8+
   python --version
   
   # Git
   git --version
   
   # Node.js (opcional, para algumas integrações)
   node --version
   
   # pip (gerenciador de pacotes Python)
   pip --version
   ```

2. **Variáveis de Ambiente**
   ```bash
   # Crie um arquivo .env na raiz do projeto
   touch .env
   
   # Exemplo de conteúdo:
   GITHUB_TOKEN=seu_token_aqui
   OPENAI_API_KEY=sua_chave_aqui
   DUCKDUCKGO_API_KEY=sua_chave_aqui
   ```

### Instalação

1. **Clone o Repositório**
   ```bash
   git clone https://github.com/seu-usuario/claude-mcp-toolkit.git
   cd claude-mcp-toolkit
   ```

2. **Ambiente Virtual**
   ```bash
   # Criar ambiente virtual
   python -m venv venv
   
   # Ativar ambiente
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Dependências**
   ```bash
   # Instalar requisitos
   pip install -r requirements.txt
   ```

### Estrutura do Projeto

```
projeto-base/
├── .env                    # Variáveis de ambiente
├── .gitignore             # Arquivos ignorados pelo git
├── README.md              # Documentação principal
├── requirements.txt       # Dependências Python
├── setup.py              # Configuração do pacote
├── src/                  # Código fonte
│   ├── __init__.py
│   ├── config.py        # Configurações
│   ├── utils/           # Utilitários
│   ├── github/          # Integrações GitHub
│   ├── apis/            # Integrações API
│   └── cli/             # Interface de linha de comando
├── tests/               # Testes
│   ├── __init__.py
│   └── test_*.py
└── docs/                # Documentação
    ├── api/
    ├── guides/
    └── examples/
```

### Configuração do Git

1. **Gitignore**
   ```gitignore
   # Python
   __pycache__/
   *.py[cod]
   *$py.class
   *.so
   .Python
   venv/
   
   # Ambiente
   .env
   .env.*
   
   # IDE
   .vscode/
   .idea/
   *.swp
   
   # Logs
   *.log
   
   # Temporários
   tmp/
   temp/
   ```

2. **Git Hooks**
   ```bash
   # Pre-commit hook para verificações
   cp templates/git-hooks/pre-commit .git/hooks/
   chmod +x .git/hooks/pre-commit
   ```

### VSCode Setup

1. **Extensões Recomendadas**
   ```json
   {
     "recommendations": [
       "ms-python.python",
       "ms-python.vscode-pylance",
       "eamodio.gitlens",
       "streetsidesoftware.code-spell-checker"
     ]
   }
   ```

2. **Configurações do Workspace**
   ```json
   {
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": true,
     "python.formatting.provider": "black",
     "editor.formatOnSave": true,
     "editor.rulers": [88],
     "files.trimTrailingWhitespace": true
   }
   ```

### Testes e Validação

1. **Executar Testes**
   ```bash
   # Instalar pytest
   pip install pytest pytest-cov
   
   # Rodar testes
   pytest
   
   # Com cobertura
   pytest --cov=src
   ```

2. **Linting**
   ```bash
   # Instalar ferramentas
   pip install black flake8 mypy
   
   # Rodar verificações
   black src/
   flake8 src/
   mypy src/
   ```

### Troubleshooting

1. **Problemas Comuns**
   - Permissões Git
   - Variáveis de ambiente
   - Dependências conflitantes
   - Versões Python incompatíveis

2. **Soluções**
   ```bash
   # Limpar cache pip
   pip cache purge
   
   # Reinstalar dependências
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   
   # Verificar ambiente
   python -m pip check
   ```

### Próximos Passos

1. **Verificação**
   - Teste configurações
   - Valide integrações
   - Verifique permissões

2. **Customização**
   - Ajuste configurações
   - Adicione dependências específicas
   - Configure hooks personalizados

3. **Desenvolvimento**
   - Crie branches
   - Implemente features
   - Execute testes

### Recursos Adicionais

- [Documentação Python](https://docs.python.org)
- [Git Documentation](https://git-scm.com/doc)
- [VSCode Python](https://code.visualstudio.com/docs/python/python-tutorial)
- [Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

### Checklist

- [ ] Python instalado e configurado
- [ ] Git instalado e configurado
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] Variáveis de ambiente configuradas
- [ ] Git hooks instalados
- [ ] IDE configurada
- [ ] Testes executados com sucesso
- [ ] Linting passando
- [ ] Documentação revisada
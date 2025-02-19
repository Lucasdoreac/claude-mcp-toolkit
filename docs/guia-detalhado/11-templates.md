# Templates e Recursos Interativos

## 📚 Modelos e Exemplos Práticos

### Links Rápidos
- [Biblioteca de Templates](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/templates)
- [Notebooks Interativos](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/notebooks)
- [Exemplos Práticos](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/examples)
- [Repositório de Componentes](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/components)

### Templates de Projeto

1. **Projeto Base Python**
   ```plaintext
   python-base/
   ├── src/
   │   ├── __init__.py
   │   ├── core/
   │   ├── utils/
   │   └── config.py
   ├── tests/
   │   ├── __init__.py
   │   └── test_core.py
   ├── docs/
   │   ├── README.md
   │   └── API.md
   ├── requirements/
   │   ├── base.txt
   │   ├── dev.txt
   │   └── prod.txt
   ├── .env.example
   ├── README.md
   ├── setup.py
   └── Makefile
   ```
   🔗 [Download Template](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/templates/python-base)

2. **API REST FastAPI**
   ```python
   # main.py
   from fastapi import FastAPI, HTTPException
   from pydantic import BaseModel
   
   app = FastAPI(
       title="API Template",
       description="Template para APIs REST com FastAPI",
       version="1.0.0"
   )
   
   @app.get("/")
   async def root():
       return {"message": "API Template"}
   
   # [Resto do código...]
   ```
   🔗 [Ver Template Completo](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/templates/fastapi-rest)

### Notebooks Interativos

1. **Análise de Dados Base**
   ```python
   # analise_base.ipynb
   {
    "cells": [
     {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
       "# Template de Análise de Dados\n",
       "\n",
       "Template base para análise de dados com pandas, numpy e matplotlib."
      ]
     },
     {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "source": [
       "import pandas as pd\n",
       "import numpy as np\n",
       "import matplotlib.pyplot as plt\n",
       "import seaborn as sns\n",
       "\n",
       "%matplotlib inline"
      ]
     }
    ]
   }
   ```
   🔗 [Abrir no Colab](https://colab.research.google.com/github/Lucasdoreac/claude-mcp-toolkit/blob/main/notebooks/analise_base.ipynb)

2. **Dashboard Interativo**
   ```python
   import streamlit as st
   import pandas as pd
   import plotly.express as px
   
   def create_dashboard():
       st.title("Dashboard Template")
       
       # Carregar dados
       data = pd.read_csv("data.csv")
       
       # Widgets interativos
       selected_column = st.selectbox(
           "Selecione a coluna",
           data.columns
       )
       
       # Gráficos
       fig = px.line(data, y=selected_column)
       st.plotly_chart(fig)
   ```
   🔗 [Ver Demo](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/templates/dashboard)

### Componentes Reutilizáveis

1. **Cliente HTTP Base**
   ```python
   from typing import Dict, Any, Optional
   import requests
   import time
   
   class BaseAPIClient:
       """
       Cliente base para APIs
       """
       def __init__(
           self,
           base_url: str,
           auth_token: Optional[str] = None,
           timeout: int = 30
       ):
           self.base_url = base_url.rstrip('/')
           self.auth_token = auth_token
           self.timeout = timeout
           self.session = requests.Session()
   
       def _get_headers(self) -> Dict[str, str]:
           headers = {'Content-Type': 'application/json'}
           if self.auth_token:
               headers['Authorization'] = f'Bearer {self.auth_token}'
           return headers
   
       def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
           url = f"{self.base_url}/{endpoint.lstrip('/')}"
           response = self.session.get(
               url,
               headers=self._get_headers(),
               params=params,
               timeout=self.timeout
           )
           response.raise_for_status()
           return response.json()
   ```
   🔗 [Ver Implementação](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/components/http_client.py)

2. **Gerenciador de Config**
   ```python
   import os
   from typing import Any, Dict
   import yaml
   from dotenv import load_dotenv
   
   class ConfigManager:
       """
       Gerenciador de configurações
       """
       def __init__(self, config_path: str = 'config.yml'):
           self.config_path = config_path
           self.config = self._load_config()
           load_dotenv()
   
       def _load_config(self) -> Dict[str, Any]:
           if os.path.exists(self.config_path):
               with open(self.config_path, 'r') as f:
                   return yaml.safe_load(f)
           return {}
   
       def get(self, key: str, default: Any = None) -> Any:
           """
           Obtém valor de configuração
           """
           # Tentar ambiente primeiro
           env_key = key.upper()
           if env_key in os.environ:
               return os.environ[env_key]
           
           # Depois arquivo de config
           return self.config.get(key, default)
   ```
   🔗 [Download](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/components/config_manager.py)

### Scripts de Utilidade

1. **Setup de Projeto**
   ```python
   #!/usr/bin/env python
   """
   Script para setup inicial de projeto
   """
   import os
   import sys
   import argparse
   from shutil import copytree
   
   def setup_project(name: str, template: str = 'python-base'):
       # Verificar template
       template_path = f"templates/{template}"
       if not os.path.exists(template_path):
           print(f"Template {template} não encontrado")
           sys.exit(1)
       
       # Criar diretório do projeto
       if os.path.exists(name):
           print(f"Diretório {name} já existe")
           sys.exit(1)
       
       # Copiar template
       copytree(template_path, name)
       
       print(f"Projeto {name} criado com sucesso!")
   
   if __name__ == "__main__":
       parser = argparse.ArgumentParser()
       parser.add_argument("name", help="Nome do projeto")
       parser.add_argument(
           "--template",
           default="python-base",
           help="Template a ser usado"
       )
       
       args = parser.parse_args()
       setup_project(args.name, args.template)
   ```
   🔗 [Ver Script](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/scripts/setup_project.py)

2. **Gerador de Documentação**
   ```python
   #!/usr/bin/env python
   """
   Gerador de documentação automática
   """
   import os
   import argparse
   from typing import List, Dict
   
   def generate_docs(
       source_dir: str,
       output_dir: str = "docs",
       template: str = "mkdocs"
   ):
       # Criar diretório de docs
       os.makedirs(output_dir, exist_ok=True)
       
       # Gerar índice
       index = []
       for root, dirs, files in os.walk(source_dir):
           for file in files:
               if file.endswith(".py"):
                   path = os.path.join(root, file)
                   index.append(path)
       
       # Gerar docs
       for file_path in index:
           generate_file_docs(file_path, output_dir, template)
   
   if __name__ == "__main__":
       parser = argparse.ArgumentParser()
       parser.add_argument("source", help="Diretório fonte")
       parser.add_argument(
           "--output",
           default="docs",
           help="Diretório de saída"
       )
       parser.add_argument(
           "--template",
           default="mkdocs",
           help="Template de documentação"
       )
       
       args = parser.parse_args()
       generate_docs(args.source, args.output, args.template)
   ```
   🔗 [Download Script](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/scripts/generate_docs.py)

### Templates de Documentação

1. **README Base**
   ```markdown
   # Nome do Projeto
   
   Descrição curta do projeto.
   
   ## 🚀 Features
   
   - Feature 1
   - Feature 2
   
   ## 📋 Pré-requisitos
   
   - Python 3.8+
   - pip
   
   ## 🔧 Instalação
   
   \```bash
   pip install -r requirements.txt
   \```
   
   ## 📖 Documentação
   
   Link para documentação completa.
   
   ## 🤝 Contribuição
   
   1. Fork o projeto
   2. Crie sua feature branch
   3. Commit suas mudanças
   4. Push para a branch
   5. Abra um Pull Request
   
   ## 📝 Licença
   
   Este projeto está sob a licença MIT.
   ```
   🔗 [Ver Template](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/templates/docs/README_template.md)

2. **Documentação API**
   ```markdown
   # API Documentation
   
   ## Endpoints
   
   ### GET /resource
   
   Descrição do endpoint.
   
   #### Parameters
   
   | Nome | Tipo | Descrição |
   |------|------|-----------|
   | param1 | string | Descrição |
   
   #### Response
   
   \```json
   {
     "id": 1,
     "name": "example"
   }
   \```
   ```
   🔗 [Template Completo](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/templates/docs/API_template.md)

### Recursos Adicionais

1. **Links Úteis**
   - [Python Docs](https://docs.python.org)
   - [FastAPI](https://fastapi.tiangolo.com)
   - [Streamlit](https://streamlit.io)
   - [Pandas](https://pandas.pydata.org)

2. **Comunidade**
   - [Discord](https://discord.gg/claude-mcp-toolkit)
   - [GitHub Discussions](https://github.com/Lucasdoreac/claude-mcp-toolkit/discussions)
   - [Stack Overflow](https://stackoverflow.com/questions/tagged/claude-mcp-toolkit)

3. **Tutoriais**
   - [Guia de Início Rápido](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/docs/quickstart.md)
   - [Melhores Práticas](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/docs/best_practices.md)
   - [Exemplos Avançados](https://github.com/Lucasdoreac/claude-mcp-toolkit/tree/main/docs/advanced.md)
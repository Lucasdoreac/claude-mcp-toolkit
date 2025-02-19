# Template Python Base

Template básico para projetos Python usando as melhores práticas.

## Estrutura

```
python-base/
├── src/                    # Código fonte
│   ├── __init__.py
│   ├── core/              # Lógica principal
│   ├── utils/             # Utilitários
│   └── config.py          # Configurações
├── tests/                 # Testes
│   ├── __init__.py
│   └── test_core.py
├── docs/                  # Documentação
├── .env.example          # Exemplo de variáveis de ambiente
├── .gitignore            # Arquivos ignorados pelo git
├── requirements.txt      # Dependências do projeto
└── setup.py             # Configuração do pacote
```

## Uso

1. Clone este template
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure o ambiente: `cp .env.example .env`
4. Execute os testes: `pytest`
5. Inicie o desenvolvimento!
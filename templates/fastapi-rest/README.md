# Template FastAPI REST

Template para APIs REST usando FastAPI com configurações completas.

## Estrutura

```
fastapi-rest/
├── app/                    # Código fonte
│   ├── __init__.py
│   ├── main.py            # Ponto de entrada
│   ├── api/               # Endpoints
│   │   ├── __init__.py
│   │   ├── v1/           # Versão 1 da API
│   │   └── deps.py       # Dependências
│   ├── core/             # Configurações core
│   ├── models/           # Modelos SQLAlchemy
│   ├── schemas/          # Schemas Pydantic
│   └── services/         # Regras de negócio
├── tests/                # Testes
│   ├── __init__.py
│   └── test_api.py
├── alembic/              # Migrações
├── docs/                 # Documentação
├── .env.example         # Exemplo de variáveis
├── docker-compose.yml   # Configuração Docker
├── Dockerfile          # Build da aplicação
└── requirements.txt    # Dependências
```

## Recursos

- FastAPI com documentação automática
- SQLAlchemy + Alembic para ORM e migrações
- Pydantic para validação de dados
- Docker + docker-compose
- Testes com pytest
- CI/CD com GitHub Actions
- Autenticação JWT
- Rate limiting
- CORS configurado
- Logging estruturado
- Métricas com Prometheus

## Uso

1. Clone o template
2. Configure o ambiente: `cp .env.example .env`
3. Inicie com Docker: `docker-compose up`
4. Acesse: http://localhost:8000/docs
# Django API Template

Template reutilizável para iniciar APIs com Django e Django REST Framework sobre uma base de infraestrutura consistente. O repositório concentra configuração, dependências e ferramentas comuns para que novos projetos possam começar pelas regras de negócio, sem recriar o bootstrap técnico.

## Estado atual: V1

A V1 entrega o bootstrap da infraestrutura: Django executado no host com uv, PostgreSQL e Redis executados pelo Docker Compose, configuração por variáveis de ambiente, migrations e testes básicos de inicialização. Integrações como autenticação, OpenAPI, Celery e cache com Redis ainda não fazem parte desta versão. O snapshot completo está em [`docs/versions/v1.md`](docs/versions/v1.md).

## Arquitetura local

```text
Linux host
├── uv + Python 3.13
│   └── Django 5.2 + Django REST Framework 3.16
└── Docker Compose
    ├── PostgreSQL 17
    └── Redis 8
```

O Django não roda em container nesta versão. Essa abordagem preserva a integração direta com IDE, debugger e hot reload durante o desenvolvimento.

## Stack

| Componente | Versão suportada |
| --- | --- |
| Python | 3.13.x |
| Django | 5.2.x LTS |
| Django REST Framework | 3.16.x |
| PostgreSQL | 17.x |
| Redis | 8.x |
| psycopg | 3.x |
| redis-py | >=6,<8 |
| django-environ | >=0.12,<1 |

As versões Python resolvidas estão registradas em `uv.lock`.

## Pré-requisitos

- Linux
- [uv](https://docs.astral.sh/uv/)
- Docker com Docker Compose
- GNU Make, opcional para usar os atalhos do `Makefile`

## Inicialização rápida com Make

Crie o arquivo de ambiente e preencha ao menos `DJANGO_SECRET_KEY` e `POSTGRES_PASSWORD`:

```bash
cp .env.example .env
```

Prepare e valide todo o ambiente:

```bash
make init
```

Esse comando sincroniza as dependências, inicia PostgreSQL e Redis, aguarda os health checks, aplica as migrations e executa os testes de configuração e conectividade.

Inicie o servidor:

```bash
make run
```

A aplicação ficará disponível em `http://127.0.0.1:8000/`.

## Inicialização manual

O uso do Make é opcional. Os comandos equivalentes são:

```bash
uv sync --locked
docker compose up -d --wait
uv run python manage.py migrate
uv run python manage.py test tests
uv run python manage.py check
uv run python manage.py runserver
```

## Variáveis de ambiente

| Variável | Finalidade | Exemplo local |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Chave criptográfica do Django | o menino ta com fome e pepe moreno insiste que ele continue a cantar |
| `POSTGRES_DB` | Nome do banco | `app` |
| `POSTGRES_USER` | Usuário do banco | `app` |
| `POSTGRES_PASSWORD` | Senha do banco | valor privado |
| `POSTGRES_HOST` | Host acessado pelo Django | `localhost` |
| `POSTGRES_PORT` | Porta publicada pelo PostgreSQL | `5432` |
| `REDIS_HOST` | Host acessado pelo cliente Redis | `localhost` |
| `REDIS_PORT` | Porta publicada pelo Redis | `6379` |
| `REDIS_DB` | Banco lógico do Redis | `0` |

O `.env` local é ignorado pelo Git. Apenas `.env.example`, sem segredos, deve ser versionado.

## Comandos disponíveis

```bash
make help
```

| Comando | Ação |
| --- | --- |
| `make init` | Prepara e valida todo o ambiente |
| `make sync` | Sincroniza dependências usando o lock |
| `make infra-up` | Inicia PostgreSQL e Redis e aguarda os health checks |
| `make infra-down` | Remove os containers preservando os volumes |
| `make status` | Exibe o estado dos containers |
| `make migrate` | Aplica as migrations |
| `make check` | Executa os checks internos do Django |
| `make test` | Executa os testes básicos de configuração |
| `make startup-test` | Testa Django, PostgreSQL e Redis em execução |
| `make run` | Inicia o servidor de desenvolvimento |

## Persistência e reset

PostgreSQL e Redis usam volumes nomeados. Parar e recriar os containers não remove os dados:

```bash
make infra-down
make infra-up
```

Para apagar completamente os dados locais e recriar o ambiente:

```bash
docker compose down -v
make init
```

> O uso de `-v` remove permanentemente os dados armazenados nos volumes locais.

## Estrutura

```text
.
├── config/              # Configuração do projeto Django
├── docs/versions/       # Snapshots arquiteturais por versão
├── tests/               # Testes básicos de inicialização
├── .env.example         # Contrato das variáveis de ambiente
├── compose.yaml         # PostgreSQL e Redis
├── Makefile             # Atalhos de desenvolvimento
├── manage.py
├── pyproject.toml
└── uv.lock
```

## Troubleshooting

- **Docker indisponível:** confirme que o daemon está ativo com `docker info`.
- **Porta 5432 ou 6379 ocupada:** altere a porta correspondente no `.env` ou encerre o serviço conflitante.
- **Credenciais do PostgreSQL alteradas:** volumes existentes preservam as credenciais usadas na primeira inicialização. Para um ambiente descartável, faça o reset com `docker compose down -v`.
- **Dependências divergentes:** execute `make sync` para restaurar o ambiente conforme o `uv.lock`.
- **Serviço não saudável:** consulte `make status` e `docker compose logs postgres redis`.

## Decisões atuais

- PostgreSQL é o único banco configurado; SQLite não é usado.
- Redis está disponível, mas ainda não está conectado ao cache, sessões ou filas.
- Os settings permanecem em um único arquivo na V1.
- Não existem abstrações genéricas de repository, service ou CRUD.
- A aplicação Django ainda não é executada em Docker.

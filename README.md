# Django API Template

Template reutilizável para APIs Django com infraestrutura local, configurações por ambiente e fundações de domínio prontas para extensão. O projeto preserva as APIs nativas do Django e do Django REST Framework, evitando camadas genéricas sem casos concretos de uso.

## Versões

### V1 — Bootstrap da infraestrutura

A V1 estabeleceu a infraestrutura mínima do template: Python e dependências gerenciados pelo uv, Django e DRF no host, PostgreSQL e Redis no Docker Compose, configuração por variáveis de ambiente, volumes persistentes, health checks e testes básicos de inicialização. Consulte o [snapshot arquitetural da V1](docs/versions/v1.md).

### V2 — Fundação da aplicação

A V2 adiciona uma aplicação headless, settings separados, models abstratas compartilhadas, custom User técnico, separação entre conta e pessoa natural e endereços com catálogo geográfico. Não existem Django Admin, templates, sessões, páginas HTML ou autenticação HTTP nesta versão. Consulte o [snapshot arquitetural da V2](docs/versions/v2.md).

### V2.1.0 — Autenticação JWT

A V2.1.0 adiciona autenticação JWT exclusivamente por email e senha, tokens de acesso e renovação, rotação com blacklist e proteção global dos endpoints. Consulte o [snapshot arquitetural da V2.1.0](docs/versions/v2.1.md).

## Stack

| Componente | Versão suportada |
| --- | --- |
| Python | 3.13.x |
| Django | 5.2.x LTS |
| Django REST Framework | 3.16.x |
| PostgreSQL | 17.x |
| Redis | 8.x |
| psycopg | >=3.2,<4 |
| redis-py | >=6,<8 |
| django-environ | >=0.12,<1 |
| Simple JWT | >=5.5,<6 |

As versões resolvidas são registradas em `uv.lock`, que deve permanecer versionado.

## Arquitetura local

```text
Linux host
├── uv + Python 3.13
│   └── Django 5.2 + DRF 3.16
└── Docker Compose
    ├── PostgreSQL 17
    └── Redis 8
```

Django executa diretamente no host para preservar debugger, integração com IDE e hot reload. Apenas PostgreSQL e Redis executam em containers.

## Pré-requisitos

- Linux;
- [uv](https://docs.astral.sh/uv/);
- Docker com Docker Compose;
- GNU Make, opcional.

## Inicialização rápida

Crie o arquivo de ambiente:

```bash
cp .env.example .env
```

Preencha pelo menos:

```dotenv
DJANGO_SECRET_KEY=uma-chave-local-segura
JWT_SIGNING_KEY=outra-chave-local-segura
POSTGRES_PASSWORD=uma-senha-local
```

Prepare e valide o ambiente:

```bash
make init
```

Esse comando sincroniza o ambiente pelo `uv.lock`, inicia PostgreSQL e Redis, aplica as migrations e executa checks e testes.

Inicie o servidor:

```bash
make run
```

Os endpoints de autenticação ficam disponíveis sob `/api/v1/auth/`. A raiz continua retornando `404`.

## Inicialização manual

```bash
uv sync --locked
docker compose up -d --wait
uv run python manage.py migrate
uv run python manage.py check
DJANGO_SETTINGS_MODULE=config.settings.test uv run python manage.py test --noinput
uv run python manage.py runserver
```

## Variáveis de ambiente

| Variável | Finalidade | Exemplo local |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Chave criptográfica do Django | valor privado |
| `DJANGO_ALLOWED_HOSTS` | Hosts aceitos em produção, separados por vírgula | `api.example.com` |
| `JWT_SIGNING_KEY` | Chave independente usada para assinar JWTs | valor privado |
| `POSTGRES_DB` | Nome do banco | `app` |
| `POSTGRES_USER` | Usuário do banco | `app` |
| `POSTGRES_PASSWORD` | Senha do banco | valor privado |
| `POSTGRES_HOST` | Host acessado pelo Django | `localhost` |
| `POSTGRES_PORT` | Porta publicada pelo PostgreSQL | `5432` |
| `REDIS_HOST` | Host acessado pelo cliente Redis | `localhost` |
| `REDIS_PORT` | Porta publicada pelo Redis | `6379` |
| `REDIS_DB` | Banco lógico do Redis | `0` |

O `.env` é local e ignorado pelo Git. Apenas `.env.example`, sem segredos, deve ser versionado.

## Comandos Make

| Comando | Ação |
| --- | --- |
| `make init` | Prepara e valida todo o ambiente |
| `make sync` | Sincroniza dependências pelo `uv.lock` |
| `make infra-up` | Inicia PostgreSQL e Redis e aguarda os health checks |
| `make infra-down` | Remove containers preservando volumes |
| `make status` | Exibe o estado dos containers |
| `make migrate` | Aplica migrations |
| `make check` | Executa o check com settings locais |
| `make check-settings` | Valida settings local, test e production |
| `make test` | Executa a suíte completa |
| `make startup-test` | Valida Django, PostgreSQL, Redis e migrations |
| `make flush-expired-tokens` | Remove tokens JWT expirados da blacklist |
| `make run` | Inicia o servidor de desenvolvimento |

## Settings

```text
config/settings/
├── base.py
├── local.py
├── test.py
└── production.py
```

- `manage.py` usa `config.settings.local`;
- a suíte usa `config.settings.test`;
- WSGI e ASGI usam `config.settings.production`;
- produção exige `DJANGO_ALLOWED_HOSTS`;
- todos os ambientes compartilham banco, aplicações e segurança básica definidos em `base.py`.

## Aplicação headless

A V2 não habilita:

- Django Admin;
- templates;
- messages;
- staticfiles;
- sessões;
- Browsable API do DRF.

O DRF renderiza somente JSON, autentica requisições com JWT e exige usuário autenticado por padrão. Endpoints públicos devem declarar `AllowAny` explicitamente.

O primeiro usuário técnico pode ser criado quando necessário:

```bash
uv run python manage.py createsuperuser
```

## Models compartilhadas

O app `core` fornece models abstratas:

- `TimeStampedModel`: `created_at` e `updated_at`;
- `ActorStampedModel`: identificação textual simples em `created_by` e `updated_by`;
- `SoftDeleteModel`: `deleted_at`, `objects`, `all_objects`, `restore()` e `hard_delete()`;
- `BaseModel`: composição padrão das três anteriores.

Use `BaseModel` como padrão. Faça herança seletiva quando uma entidade não puder usar algum desses comportamentos.

Soft delete possui limitações deliberadas:

- não existe cascade lógico automático;
- registros excluídos continuam ocupando constraints únicas;
- `on_delete` é acionado somente por exclusão física;
- campos de ator não substituem uma solução completa de auditoria.

## Contas e pessoas

```text
accounts.User ← people.NaturalPerson
```

`accounts.User` representa a identidade técnica: email, senha, estado da conta, grupos e permissões. Ele herda de `AbstractUser`, remove `username` e os campos civis `first_name` e `last_name` e permanece compatível com `authenticate()`, `get_user_model()` e `createsuperuser`. O email é a única forma de login, é obrigatório e único sem diferenciar maiúsculas.

`people.NaturalPerson` representa a pessoa real. Ela possui `full_name`, `birth_date`, idade calculada e uma relação um-para-um protegida com o User. Um User pode existir sem pessoa natural.

## Autenticação JWT

Obtenha um par de tokens usando email e senha:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"secret"}'
```

Use o access token em endpoints protegidos:

```http
Authorization: Bearer <access-token>
```

Renove o par enviando o refresh atual para `POST /api/v1/auth/token/refresh/`. A renovação rotaciona o refresh e invalida o anterior. Access tokens duram 15 minutos e refresh tokens, 7 dias.

Em produção, disponibilize a API somente por HTTPS e execute periodicamente `make flush-expired-tokens` para remover registros expirados da blacklist.

## Endereços

```text
Country
└── State
    └── City
        └── BaseAddress (abstrata)
            └── NaturalPersonAddress
```

`Country`, `State` e `City` são catálogos protegidos por FKs e constraints de unicidade. Eles possuem timestamps e atores, mas não soft delete. Para inativação futura, prefira um estado explícito em vez de ocultar uma localidade ainda referenciada.

`BaseAddress` contém cidade, código postal, logradouro, número, complemento e bairro. `NaturalPersonAddress` liga esses dados a uma pessoa por `ForeignKey`, permitindo múltiplos endereços. A propriedade `full_address` monta a representação completa sem persistir dados geográficos duplicados.

A relação permite `0..N` endereços no banco. Uma regra exigindo ao menos um endereço deve ser aplicada futuramente no fluxo de criação da pessoa.

## Migrations

As migrations fazem parte do código e devem ser versionadas:

```bash
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py migrate
uv run python manage.py showmigrations
```

Ao migrar de uma instalação local da V1 para a V2, recrie o banco porque a V1 aplicou migrations usando `auth.User`:

```bash
docker compose down -v
make init
```

Esse comando remove permanentemente os dados dos volumes locais.

## Persistência

Parar os containers preserva os dados:

```bash
make infra-down
make infra-up
```

Para reiniciar completamente:

```bash
docker compose down -v
make init
```

## Estrutura

```text
.
├── apps/
│   ├── accounts/
│   ├── addresses/
│   ├── core/
│   └── people/
├── config/settings/
├── docs/versions/
├── tests/
├── compose.yaml
├── Makefile
├── manage.py
├── pyproject.toml
└── uv.lock
```

## Troubleshooting

- **Migration inconsistente após a V1:** remova os volumes locais e recrie o banco.
- **Porta 5432 ou 6379 ocupada:** altere a porta no `.env` ou encerre o serviço conflitante.
- **Credenciais PostgreSQL alteradas:** volumes existentes preservam as credenciais originais; recrie-os se forem descartáveis.
- **Settings de produção falhando:** configure `DJANGO_ALLOWED_HOSTS`.
- **Serviço não saudável:** execute `make status` e consulte `docker compose logs postgres redis`.
- **Dependências divergentes:** execute `make sync`.

## Fora do escopo da V2

- endpoints de autenticação e JWT;
- serializers e ViewSets;
- OpenAPI e CORS;
- Celery e integração do Redis;
- padrão global de erros;
- CI/CD;
- Docker da aplicação Django;
- abstrações genéricas de repository, service ou CRUD.

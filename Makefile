UV_RUN := uv run
MANAGE := $(UV_RUN) python manage.py

.DEFAULT_GOAL := help

.PHONY: help sync infra-up infra-down status migrate check check-settings test startup-test init run

help:
	@echo "Comandos disponíveis:"
	@echo "  make init          Prepara e valida todo o ambiente local"
	@echo "  make sync          Sincroniza as dependências pelo uv.lock"
	@echo "  make infra-up      Sobe PostgreSQL e Redis e aguarda os health checks"
	@echo "  make infra-down    Remove os containers preservando os volumes"
	@echo "  make status        Exibe o estado dos containers"
	@echo "  make migrate       Aplica as migrations do Django"
	@echo "  make check         Executa os checks internos do Django"
	@echo "  make check-settings Valida os settings local, test e production"
	@echo "  make test          Executa a suíte completa de testes"
	@echo "  make startup-test  Valida Django, PostgreSQL e Redis em execução"
	@echo "  make run           Inicia o servidor de desenvolvimento"

sync:
	uv sync --locked

infra-up:
	docker compose up -d --wait

infra-down:
	docker compose down

status:
	docker compose ps

migrate:
	$(MANAGE) migrate

check:
	$(MANAGE) check

check-settings:
	$(MANAGE) check --settings=config.settings.local
	$(MANAGE) check --settings=config.settings.test
	DJANGO_ALLOWED_HOSTS=example.com $(MANAGE) check --settings=config.settings.production

test:
	DJANGO_SETTINGS_MODULE=config.settings.test $(MANAGE) test --noinput

startup-test: check-settings
	docker compose config --quiet
	docker compose exec -T postgres sh -c 'pg_isready -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'
	docker compose exec -T redis redis-cli ping
	$(MANAGE) migrate --check
	$(MANAGE) shell -c "from django.db import connection; connection.ensure_connection(); print('PostgreSQL via Django: OK')"
	$(UV_RUN) python -c "from pathlib import Path; import environ, redis; env = environ.Env(); environ.Env.read_env(Path('.env')); client = redis.Redis(host=env('REDIS_HOST'), port=env.int('REDIS_PORT', default=6379), db=env.int('REDIS_DB', default=0)); assert client.ping(); print('Redis via Python: OK')"

init:
	$(MAKE) sync
	$(MAKE) infra-up
	$(MAKE) migrate
	$(MAKE) test
	$(MAKE) startup-test

run:
	$(MANAGE) runserver

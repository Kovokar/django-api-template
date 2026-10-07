# Graph Report - django-api-template  (2026-10-06)

## Corpus Check
- Corpus is ~2,812 words - fits in a single context window. You may not need a graph.

## Summary
- 126 nodes · 156 edges · 19 communities (10 shown, 9 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 21 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- V1 Architecture and Docs
- Soft Delete Query Layer
- Core Abstract Models
- Docker Infrastructure
- Django Entrypoints
- Environment Settings
- Startup Configuration Tests
- Core Integration Tests
- Agent Collaboration Rules
- Core App Configuration
- URL Routing
- Project Metadata

## God Nodes (most connected - your core abstractions)
1. `V1 — Bootstrap da infraestrutura` - 12 edges
2. `SoftDeleteModel` - 10 edges
3. `SoftDeleteQuerySet` - 9 edges
4. `AbstractModelsTests` - 8 edges
5. `CoreModelsIntegrationTests` - 8 edges
6. `StartupConfigurationTests` - 6 edges
7. `Django API Template` - 6 edges
8. `SoftDeleteManager` - 5 edges
9. `TimeStampedModel` - 5 edges
10. `ActorStampedModel` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Escopo incremental sem abstrações prematuras` --semantically_similar_to--> `Base mínima para APIs Django`  [INFERRED] [semantically similar]
  AGENTS.md → docs/versions/v1.md
- `Bootstrap de infraestrutura V1` --semantically_similar_to--> `Base mínima para APIs Django`  [INFERRED] [semantically similar]
  README.md → docs/versions/v1.md
- `Django executado no host` --semantically_similar_to--> `Django no host e infraestrutura no Compose`  [INFERRED] [semantically similar]
  README.md → docs/versions/v1.md
- `Redis disponível mas não integrado` --semantically_similar_to--> `Redis ainda não integrado`  [INFERRED] [semantically similar]
  README.md → docs/versions/v1.md
- `Settings em arquivo único` --semantically_similar_to--> `Settings único na V1`  [INFERRED] [semantically similar]
  README.md → docs/versions/v1.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Arquitetura local da V1** — readme_django_no_host, compose_postgres_service, compose_redis_service [INFERRED 0.95]
- **Validação da infraestrutura V1** — docs_versions_v1_fluxo_make_init, compose_postgres_healthcheck, compose_redis_healthcheck [INFERRED 0.85]

## Communities (19 total, 9 thin omitted)

### Community 0 - "V1 Architecture and Docs"
Cohesion: 0.14
Nodes (18): Escopo incremental sem abstrações prematuras, APIs nativas de Django e DRF preservadas, Django no host e infraestrutura no Compose, Base mínima para APIs Django, Checklist da V1, V1 — Bootstrap da infraestrutura, Funcionalidades fora da V1, Redis ainda não integrado (+10 more)

### Community 1 - "Soft Delete Query Layer"
Cohesion: 0.24
Nodes (7): AllObjectsManager, SoftDeleteManager, SoftDeleteQuerySet, _update_timestamp_if_available(), django_core_exceptions, django_db, django_utils

### Community 2 - "Core Abstract Models"
Cohesion: 0.22
Nodes (8): ActorStampedModel, Meta, SoftDeleteModel, TimeStampedModel, AbstractModelsTests, CoreTestModel, Meta, SimpleTestCase

### Community 3 - "Docker Infrastructure"
Cohesion: 0.17
Nodes (15): Stack Docker Compose, Contrato de ambiente do Compose, Volume postgres_data, Health check do PostgreSQL, Serviço PostgreSQL 17, Volume redis_data, Health check do Redis, Serviço Redis 8 (+7 more)

### Community 4 - "Django Entrypoints"
Cohesion: 0.17
Nodes (9): ASGI config for config project. It exposes the ASGI callable as a module-level…, WSGI config for config project. It exposes the WSGI callable as a module-level…, django_core_asgi, django_core_wsgi, main(), Django's command-line utility for administrative tasks., Run administrative tasks., os (+1 more)

### Community 5 - "Environment Settings"
Cohesion: 0.20
Nodes (6): Settings shared by every environment., Settings for local development., Settings for production environments., Settings for the automated test suite., environ, pathlib

### Community 6 - "Startup Configuration Tests"
Cohesion: 0.22
Nodes (4): django_conf, django_test, SimpleTestCase, StartupConfigurationTests

### Community 8 - "Agent Collaboration Rules"
Cohesion: 0.29
Nodes (7): Atualização do grafo após mudanças, Autorização explícita para implementação, Consulta dirigida ao grafo, Diretrizes de colaboração, Graphify, Inspeções não destrutivas, Orientação e revisão técnica

### Community 9 - "Core App Configuration"
Cohesion: 0.50
Nodes (3): AppConfig, CoreConfig, django_apps

### Community 10 - "URL Routing"
Cohesion: 0.50
Nodes (3): URL configuration for config project. The `urlpatterns` list routes URLs to…, django_contrib, django_urls

## Knowledge Gaps
- **7 isolated node(s):** `Meta`, `django-api-template`, `Configuração por variáveis de ambiente`, `Inicialização e validação com Make`, `Checklist da V1` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 53 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `V1 — Bootstrap da infraestrutura` connect `V1 Architecture and Docs` to `Docker Infrastructure`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Why does `CoreModelsIntegrationTests` connect `Core Integration Tests` to `Core Abstract Models`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `SoftDeleteModel` connect `Core Abstract Models` to `Soft Delete Query Layer`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `SoftDeleteModel` (e.g. with `AllObjectsManager` and `SoftDeleteManager`) actually correct?**
  _`SoftDeleteModel` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SoftDeleteQuerySet` (e.g. with `AllObjectsManager` and `SoftDeleteManager`) actually correct?**
  _`SoftDeleteQuerySet` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `AbstractModelsTests` (e.g. with `ActorStampedModel` and `SoftDeleteModel`) actually correct?**
  _`AbstractModelsTests` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Meta`, `django-api-template`, `Configuração por variáveis de ambiente` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._
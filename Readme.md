# Backend Central de Talentos

## Criar um novo app no projeto
```bash
django-admin startapp name-of-app
```

## Rodar Aplicação Localmente sem Docker
[Guia para rodar localmente sem Docker](docs/how_to_run_local_without_docker.md)

## Rodar Aplicação Localmente com Docker
[Guia para rodar localmente com Docker](docs/how_to_run_local_with_docker.md)

## Logs
[Guia para visualizar logs em Prod](docs/how_to_get_logs.md)

## Testes
[Guia de Execução dos Testes Automatizados](docs/tests.md)

## Running 1 app
- docker-compose run --rm tests coverage run manage.py test access

## Running 1 test:
- docker-compose run --rm tests coverage run manage.py test access.tests.UserViewSetTest.test_list_users_success

### Gerar relatório
- docker-compose run --rm tests coverage html


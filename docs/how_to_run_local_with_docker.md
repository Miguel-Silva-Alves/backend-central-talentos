# Guia para rodar a Aplicação localmente com Docker

## Subir a aplicação

```bash
git pull origin main
```

```bash
docker-compose up -d --build
```

## Matar a Aplicação

```bash
docker-compose down
```

## Executar migrações

Para executar migrações, a aplicação deve estar ativa (em execução). 

```bash
docker-compose exec web python manage.py migrate --noinput
```

## Criar superuser do Django

Para criar um superuser, a aplicação deve estar ativa (em execução). 

```bash
docker-compose exec web python manage.py createsuperuser
```
# Guia para rodar a Aplicação localmente sem Docker

## Instalar dependências necessárias para rodar a aplicação

```bash
python -m venv venv
```

```bash
source venv/bin/activate
```

```bash
cd app/
```

```bash
pip install -r requirements.txt
```

## Rodar a aplicação

```bash
source venv/bin/activate
```

```bash
cd app/
```

```bash
python manage.py runserver
```

## Criar migrações

```bash
source venv/bin/activate
```

```bash
cd app/
```

```bash
python manage.py makemigrations
```

## Executar migrações

```bash
source venv/bin/activate
```

```bash
cd app/
```

```bash
python manage.py migrate --noinput
```

## Criar superuser do Django

```bash
source venv/bin/activate
```

```bash
cd app/
```

```bash
python manage.py createsuperuser
```
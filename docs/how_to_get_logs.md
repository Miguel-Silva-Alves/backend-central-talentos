# 📄 Acessando logs em produção

## 🔍 Logs no console (tempo real)
Para acompanhar os logs de execução (Gunicorn e prints do Django):

```bash
docker logs -f backend-movement
```

## 📂 Logs gravados em arquivo (LOGGING_DIR)
O Django está configurado para salvar logs no diretório:

### Visualizar dentro do container:
```
docker exec -it backend-movement tail -f /home/app/web/logs/django.log
```

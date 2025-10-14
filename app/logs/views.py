# Models
from logs.models import Log

# Settings
from project.settings import DEBUG

#LOGS 
import logging
logger = logging.getLogger(__name__)

# Create your views here.
from datetime import datetime


def saveLog(msg, type = "Error", path=None):

    try:
        msg = str(msg)
        Log.objects.create(
            msg=msg,
            typed=type,
            path=path
        )
        if DEBUG == 1:
            current_time = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")  # Formato de data e hora
            print(f'{current_time} DEB {msg}')
    except Exception as e:
        logger.error("Erro ao criar o log: " + str(e))


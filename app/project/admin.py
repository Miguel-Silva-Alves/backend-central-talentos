from django.contrib.admin.sites import AdminSite
from django.db import connection
from django.contrib import admin
from django.contrib.auth.models import User, Group

#LOGS 
import logging
logger = logging.getLogger(__name__)

def consulta():

        cursor = connection.cursor()
        try:
            cursor.execute(
                '''
                select table_name, pg_size_pretty( pg_relation_size(quote_ident(table_name)) )
                from information_schema.tables
                where table_schema = 'public'
                order by pg_relation_size(quote_ident(table_name)) desc;
                '''
            )
            retorno = cursor.fetchall()
            return {tupla[0]: tupla[1] for tupla in retorno}
        except Exception as e:
            logger.error(str(e))
        return {}
        

class CustomAdminSite(AdminSite):     

    def get_app_list(self, request):
        
        app_list = super().get_app_list(request)
        tamanhos = consulta()
        print('tamanhos:', tamanhos)
        for app in app_list:
            if 'models' in app:
                for model in app['models']:
                    string = str(model['model']).replace("<class '", "")
                    string = string.replace("'>", '')
                    string = string.replace(".models.", "_").lower()
            
                    print(string)
                    
                    model['size'] = tamanhos.get(string, 'Não identificado')
        return app_list
        
# admin.site = CustomAdminSite(name='customadminsite')



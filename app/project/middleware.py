import logging
import json
import traceback
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.db import transaction

from logs.models import RequestDebugLog

logger = logging.getLogger(__name__)

class RequestDebugMiddleware(MiddlewareMixin):
    """
    Middleware para capturar e logar informações detalhadas de requests 
    que não retornam status codes de sucesso (200-299).
    """
    
    def process_request(self, request):
        """Captura informações iniciais da request"""
        request._debug_start_time = timezone.now()
        return None
    
    def process_response(self, request, response):
        """Processa a resposta e loga informações se não for sucesso"""
        
        # Só processa se não for status de sucesso (200-299)
        if not (200 <= response.status_code < 300):
            self._log_request_details(request, response)
        
        return response
    
    def process_exception(self, request, exception):
        """Processa exceções não tratadas"""
        self._log_request_details(request, None, exception)
        return None  # Deixa o Django tratar a exceção normalmente
    
    def _log_request_details(self, request, response=None, exception=None):
        """Loga informações detalhadas da request"""
        
        try:
            # Informações básicas da request
            user_obj = None
            user_str = 'Anonymous'
            
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_obj = request.user
                user_str = str(request.user)
            
            request_info = {
                'timestamp': timezone.now().isoformat(),
                'method': request.method,
                'path': request.path,
                'full_path': request.get_full_path(),
                'user': user_str,
                'remote_addr': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referer': request.META.get('HTTP_REFERER', ''),
                'content_type': request.META.get('CONTENT_TYPE', ''),
                'content_length': request.META.get('CONTENT_LENGTH', ''),
            }
            
            # Headers da request (filtrando headers sensíveis)
            headers = {}
            for key, value in request.META.items():
                if key.startswith('HTTP_'):
                    header_name = key[5:].replace('_', '-').title()
                    # Filtra headers sensíveis
                    if header_name.lower() not in ['authorization', 'cookie', 'x-api-key']:
                        headers[header_name] = value
            
            request_info['headers'] = headers
            
            # Query parameters
            if request.GET:
                request_info['query_params'] = dict(request.GET.items())
            
            # Request body (limitando tamanho)
            body_content = ''
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    if hasattr(request, 'body') and request.body:
                        body = request.body.decode('utf-8')
                        # Limita o tamanho do body para evitar logs gigantes
                        if len(body) > 5000:
                            body = body[:5000] + '... [TRUNCATED]'
                        body_content = body
                        
                        # Tenta parsear como JSON se possível
                        try:
                            request_info['body_json'] = json.loads(body)
                        except json.JSONDecodeError:
                            request_info['body_raw'] = body
                except Exception:
                    request_info['body_error'] = 'Could not decode request body'
                    body_content = 'Could not decode request body'
            
            # POST data (formulários)
            if request.method == 'POST' and request.POST:
                post_data = {}
                for key, value in request.POST.items():
                    # Filtra campos sensíveis
                    if key.lower() not in ['password', 'token', 'api_key']:
                        post_data[key] = value
                request_info['post_data'] = post_data
            
            # Informações da resposta
            response_content = ''
            status_code = None
            reason_phrase = ''
            response_content_type = ''
            
            if response:
                status_code = response.status_code
                reason_phrase = response.reason_phrase
                response_content_type = response.get('Content-Type', '')
                
                response_info = {
                    'status_code': status_code,
                    'reason_phrase': reason_phrase,
                    'content_type': response_content_type,
                }
                
                # Tenta capturar conteúdo da resposta (limitado)
                if hasattr(response, 'content'):
                    try:
                        content = response.content.decode('utf-8')
                        if len(content) > 2000:
                            content = content[:2000] + '... [TRUNCATED]'
                        response_content = content
                        
                        # Tenta parsear como JSON se possível
                        try:
                            response_info['content_json'] = json.loads(content)
                        except json.JSONDecodeError:
                            response_info['content_raw'] = content
                    except Exception:
                        response_info['content_error'] = 'Could not decode response content'
                        response_content = 'Could not decode response content'
                
                request_info['response'] = response_info
            
            # Informações da exceção
            exception_type = ''
            exception_message = ''
            exception_traceback = ''
            
            if exception:
                exception_type = type(exception).__name__
                exception_message = str(exception)
                exception_traceback = traceback.format_exc()
                
                exception_info = {
                    'type': exception_type,
                    'message': exception_message,
                    'traceback': exception_traceback
                }
                request_info['exception'] = exception_info
            
            # Tempo de processamento
            processing_time_ms = None
            if hasattr(request, '_debug_start_time'):
                processing_time = timezone.now() - request._debug_start_time
                processing_time_ms = processing_time.total_seconds() * 1000
                request_info['processing_time_ms'] = processing_time_ms
            
            # Determina o nível de log baseado no status ou exceção
            if exception:
                log_level = logging.ERROR
                log_level_str = 'ERROR'
                log_message = f"REQUEST EXCEPTION: {request.method} {request.path} - {type(exception).__name__}: {str(exception)}"
            elif response and response.status_code >= 500:
                log_level = logging.ERROR
                log_level_str = 'ERROR'
                log_message = f"REQUEST ERROR: {request.method} {request.path} - Status: {response.status_code}"
            elif response and response.status_code >= 400:
                log_level = logging.WARNING
                log_level_str = 'WARNING'
                log_message = f"REQUEST WARNING: {request.method} {request.path} - Status: {response.status_code}"
            else:
                log_level = logging.INFO
                log_level_str = 'INFO'
                log_message = f"REQUEST INFO: {request.method} {request.path}"
            
            # Salva no banco de dados
            try:
                with transaction.atomic():
                    RequestDebugLog.objects.create(
                        method=request.method,
                        path=request.path,
                        full_path=request.get_full_path(),
                        user=user_obj,
                        user_str=user_str,
                        remote_addr=self._get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:2000],  # Limita tamanho
                        referer=request.META.get('HTTP_REFERER', '')[:2000],
                        headers=headers,
                        query_params=dict(request.GET.items()) if request.GET else {},
                        post_data=post_data if request.method == 'POST' and request.POST else {},
                        body_content=body_content[:10000],  # Limita tamanho do body
                        content_type=request.META.get('CONTENT_TYPE', ''),
                        content_length=request.META.get('CONTENT_LENGTH', ''),
                        status_code=status_code,
                        reason_phrase=reason_phrase,
                        response_content_type=response_content_type,
                        response_content=response_content[:10000],  # Limita tamanho da resposta
                        exception_type=exception_type,
                        exception_message=exception_message[:2000],  # Limita mensagem
                        exception_traceback=exception_traceback[:10000],  # Limita traceback
                        processing_time_ms=processing_time_ms,
                        log_level=log_level_str
                    )
            except Exception as db_error:
                # Se falhar ao salvar no banco, só loga o erro
                # logger.error(f"Failed to save RequestDebugLog to database: {str(db_error)}")
                pass
            
            # Loga as informações no console/arquivo
            # logger.log(
            #     log_level,
            #     f"{log_message}\nRequest Details: {json.dumps(request_info, indent=2, ensure_ascii=False)}"
            # )
            
        except Exception as e:
            # Fallback caso o próprio middleware falhe
            logger.error(f"RequestDebugMiddleware failed to log request: {str(e)}")
    
    def _get_client_ip(self, request):
        """Obtém o IP real do cliente considerando proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
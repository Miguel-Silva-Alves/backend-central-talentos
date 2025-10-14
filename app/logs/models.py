from django.db import models
from access.models import User

# Create your models here.
class Log(models.Model):
    msg_type = [
        ('Warning', 'Warning'),
        ('Print', 'Print'),
        ('Error', 'Error'),
        ('Confirm', 'Confirm'),
        ('OK', 'OK')
    ]
    created_at = models.DateTimeField(auto_now=True, editable=True)
    msg = models.TextField(null=True)
    typed = models.CharField(
        max_length=20,
        choices=msg_type,
        default='OK'
    )
    path=models.CharField(max_length=255,null=True, default=None)

    def __str__(self) -> str:
        return self.typed + " - " + self.msg

class RequestDebugLog(models.Model):
    """
    Modelo para armazenar logs detalhados de requests que falharam
    """
    
    # Identificação
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Request Info
    method = models.CharField(max_length=10)
    path = models.TextField()
    full_path = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_str = models.CharField(max_length=255, null=True, blank=True)  # Fallback se user for None
    remote_addr = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referer = models.TextField(blank=True)
    
    # Request Details
    headers = models.JSONField(default=dict, blank=True)
    query_params = models.JSONField(default=dict, blank=True)
    post_data = models.JSONField(default=dict, blank=True)
    body_content = models.TextField(blank=True)  # Para body JSON ou raw
    content_type = models.CharField(max_length=100, blank=True)
    content_length = models.CharField(max_length=20, blank=True)
    
    # Response Info
    status_code = models.IntegerField(null=True, blank=True)
    reason_phrase = models.CharField(max_length=100, blank=True)
    response_content_type = models.CharField(max_length=100, blank=True)
    response_content = models.TextField(blank=True)
    
    # Exception Info
    exception_type = models.CharField(max_length=100, blank=True)
    exception_message = models.TextField(blank=True)
    exception_traceback = models.TextField(blank=True)
    
    # Performance
    processing_time_ms = models.FloatField(null=True, blank=True)
    
    # Classification
    log_level = models.CharField(max_length=20, default='INFO')  # INFO, WARNING, ERROR
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['status_code']),
            models.Index(fields=['method']),
            models.Index(fields=['log_level']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code or 'Exception'} ({self.timestamp})"
    
    @property
    def is_error(self):
        return self.log_level == 'ERROR'
    
    @property
    def is_warning(self):
        return self.log_level == 'WARNING'
    
    @property
    def has_exception(self):
        return bool(self.exception_type)
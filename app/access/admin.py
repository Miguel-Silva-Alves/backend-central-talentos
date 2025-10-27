from django.contrib import admin
from access.models import RefreshToken, Token, User, GoogleAuthentication, EmailPasswordAuthentication, RecoveryPassword, ValidateEmail
from common.exportCSV import export_to_csv


class UserAdminCustom(admin.ModelAdmin):
    list_display=('email','is_staff','id')
    list_filter = ['is_staff',]
    search_fields = ('username', 'email')  
    actions=[export_to_csv]

class TokenAdmin(admin.ModelAdmin):
    list_display=('user', 'iat', 'expires_at')    
    actions=[export_to_csv]

class RefreshTokenAdmin(admin.ModelAdmin):
    list_display=('get_user', 'iat', 'expires_at')    
    actions=[export_to_csv]

    def get_user(self, obj: RefreshToken):
        if obj.token.user:
            return obj.token.user
        return "No User"

class RecuperarSenhaAdmin(admin.ModelAdmin):
    list_display=('user', 'code', 'created_at')    
    actions=[export_to_csv]

class SmartwatchAdminCustom(admin.ModelAdmin):
    list_display=('uuid','id_android','student')
    search_fields = ['student','id_android'] 
    actions=[export_to_csv]

class ValidateEmailAdmin(admin.ModelAdmin):
    list_display=('id', 'email', 'code','is_active')
    search_fields = ['email'] 

admin.site.register(Token,TokenAdmin)
admin.site.register(RefreshToken, RefreshTokenAdmin)
admin.site.register(User,UserAdminCustom)
admin.site.register(GoogleAuthentication)
admin.site.register(EmailPasswordAuthentication)
admin.site.register(RecoveryPassword, RecuperarSenhaAdmin)
admin.site.register(ValidateEmail, ValidateEmailAdmin)

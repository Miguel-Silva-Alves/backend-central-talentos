from datetime import timedelta

from django.utils import timezone
from django.db import models
from django.utils.timezone import now
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

# Models
from company.models import Company       # importa seu model Company


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, null=True, blank=True, default=None)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)

    # 🔗 relação com a empresa
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,  # se a empresa for deletada, mantém o user sem empresa
        null=True,
        blank=True,
        related_name='users'
    )

    USERNAME_FIELD = "email"
    objects = CustomUserManager()

    groups = models.ManyToManyField(
        'auth.Group',
        related_name="access_user_groups",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name="access_user_permissions",
        blank=True,
    )

    def __str__(self):
        return f"{self.email} ({self.company.name if self.company else 'sem empresa'})"

    # --- métodos do diagrama ---
    def validate_credentials(self, username: str, password: str) -> bool:
        """Valida credenciais manualmente (apenas exemplo; o Django faz isso nativo)."""
        return self.username == username and self.check_password(password)

    def update_password(self, new_password: str) -> None:
        """Atualiza a senha com o hash correto."""
        self.set_password(new_password)
        self.save(update_fields=['password'])

    def display_name(self) -> str:
        """Retorna o nome formatado para exibição."""
        return self.username or self.email
    
class Authentication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()

    class Meta:
        abstract = True

class EmailPasswordAuthentication(Authentication):
    password = models.CharField(max_length=128)
    def __str__(self):
        return self.email

class FacebookAuthentication(Authentication):
    facebook_password = models.CharField(max_length=128)
    def __str__(self):
        return self.email

class GoogleAuthentication(Authentication):
    client_id = models.CharField(max_length=128)
    sid = models.CharField(max_length=128)

    def __str__(self):
        return self.email
    
def default_expiration():
    return timezone.now() + timedelta(hours=1)
class Token(models.Model):
    token = models.CharField(max_length=256) 
    iat = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=default_expiration)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def is_valid(self):
        return self.expires_at > timezone.localtime(timezone.now())
    
    def __str__(self):
        return f"{self.iat.strftime('%d/%m/%y')} - {self.expires_at.strftime('%d/%m/%y')}"
    
class RefreshToken(models.Model):
    refresh_token = models.CharField(max_length=256) 
    iat = models.DateTimeField()
    expires_at = models.DateTimeField()
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    
    def is_valid(self):
        return self.expires_at > timezone.localtime(timezone.now())

    def __str__(self):
        return self.iat.strftime('%d/%m/%y') + ' - ' + self.expires_at.strftime('%d/%m/%y')
    

class RecoveryPassword(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + ' - ' + str(self.is_active)

    def is_valid(self) -> bool:

        now = timezone.now()
        expiration_time = self.created_at + timezone.timedelta(minutes=15)
        print('CRIADO', self.created_at, 'EXPIRACAO', expiration_time)
        if now >= expiration_time:

            self.invalidate()
            return False
        return True

    def invalidate(self):
        self.is_active = False
        self.save()

    def delete_me(self):
        self.delete()

class ValidateEmail(models.Model):

    email = models.EmailField()
    code = models.CharField(max_length=6, validators=[MinLengthValidator(6)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.email + ' - ' + str(self.is_active)

    def is_valid(self) -> bool:

        now = timezone.now()
        expiration_time = self.created_at + timezone.timedelta(hours=1)
        print('CRIADO', self.created_at, 'EXPIRACAO', expiration_time)
        if now >= expiration_time:

            self.invalidate()
            return False
        return True
    
    def invalidate(self):
        self.is_active = False
        self.save()


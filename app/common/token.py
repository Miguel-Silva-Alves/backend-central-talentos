from functools import wraps
from django.utils import timezone
from access.models import Token, RefreshToken, User
from common.response import UnauthorizedRequest
from project.settings import X_API_KEY


class TokenValidator:
    """
    Classe responsável por validar tokens, refresh tokens e API keys.
    Inclui decorators internos para proteger endpoints.
    """

    def check_token(self, token_str: str) -> bool:
        try:
            token = Token.objects.get(token=token_str)
        except Token.DoesNotExist:
            return False
        return token.expires_at > timezone.now()

    def check_refresh_token(self, refresh_token_str: str) -> bool:
        try:
            refresh_token = RefreshToken.objects.get(refresh_token=refresh_token_str)
        except RefreshToken.DoesNotExist:
            return False
        return refresh_token.expires_at > timezone.now()

    def check_x_api_key(self, api_key_str: str) -> bool:
        valid_api_keys = [X_API_KEY]
        return api_key_str in valid_api_keys

    # ---------------------------
    # Decorators internos
    # ---------------------------

    @classmethod
    def require_x_api_key(cls, func):
        """
        Decorator para exigir e validar header x-api-key.
        """
        @wraps(func)
        def wrapper(viewset, request, *args, **kwargs):
            api_key = request.headers.get("x-api-key")
            validator = cls()
            if not api_key or not validator.check_x_api_key(api_key):
                return UnauthorizedRequest("Invalid or missing x-api-key")
            return func(viewset, request, *args, **kwargs)
        return wrapper

    @classmethod
    def require_token(cls, func):
        """
        Decorator para exigir e validar Bearer Token.
        Injeta o user autenticado e o token em request.
        """
        @wraps(func)
        def wrapper(viewset, request, *args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                return UnauthorizedRequest("Missing Authorization header")

            token_str = auth_header.split(" ")[1]

            try:
                token = Token.objects.select_related("user").get(token=token_str)
            except Token.DoesNotExist:
                return UnauthorizedRequest("Invalid token")

            if token.expires_at < timezone.now():
                return UnauthorizedRequest("Expired token")

            # injeta dados no request
            request.token = token
            request.user = token.user

            return func(viewset, request, *args, **kwargs)
        return wrapper

from functools import wraps
from common.response import UnauthorizedRequest
from simplejwt.jwt import encode, decode
from project.settings import SECRET_KEY as secret

# Models
from access.models import Token, RefreshToken, User

# Log
from logs.views import saveLog
from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())

# Datetime
from django.utils import timezone
from datetime import timedelta

# Typing
from typing import Tuple

# Create token after user is authenticated (login) or aumenta o tempo dele


def create_token(user, is_to_refactor_token=False):
    token_object = Token.objects.filter(user=user).first()
   
    current_time = timezone.now()
    exp_date = current_time + timedelta(days=90)


    if not token_object or is_to_refactor_token:
        token = encode_token(email=user.email, user_id=user.id,
                             iat=current_time.timestamp(), exp=exp_date.timestamp())
        try:
            token_object = Token.objects.create(
                user=user,
                expires_at=exp_date,
                token=token,
                iat=current_time
            )

            refresh_token = encode_token(iat=current_time.timestamp(), exp=exp_date.timestamp())
            exp_date = current_time + timedelta(days=7)
            try:
                rf_token = RefreshToken.objects.create(
                    token=token_object,
                    refresh_token=refresh_token,
                    expires_at=exp_date,
                    iat=current_time
                )
            except Exception as e:
                saveLog(str(e), type="Error", path=f'File path: {frameinfo.filename}; At line: {frameinfo.lineno}')
                return False, None, None
        except Exception as e:
            saveLog(str(e), type="Error", path=f'File path: {frameinfo.filename}; At line: {frameinfo.lineno}')
            return False, None, None
        return True, token_object, rf_token
    
    is_to_refactor, exp_date = verify_expiration(token_object)
    rf_token = RefreshToken.objects.filter(token=token_object).first()

    if not rf_token:
        refresh_token = encode_token(iat=current_time.timestamp(), exp=exp_date.timestamp())
        exp_date = current_time + timedelta(days=7)
        rf_token = RefreshToken.objects.create(
            token=token_object,
            refresh_token=refresh_token,
            expires_at=exp_date,
            iat=current_time
        )

    if is_to_refactor:
        token = encode_token(email=user.email, user_id=user.pk,
                             iat=current_time.timestamp(), exp=exp_date.timestamp())
        token_object.token = token
        token_object.iat = current_time
        token_object.expires_at = exp_date
        token_object.save()

        exp_date = current_time + timedelta(days=7)
        new_rft = encode_token(iat=current_time.timestamp(), exp=exp_date.timestamp())
        rf_token.refresh_token = new_rft
        rf_token.iat = current_time
        rf_token.expires_at = exp_date
        rf_token.save()

    return True, token_object, rf_token

def refresh_token(token: str, refresh_token: str):
        
    token_object = Token.objects.filter(token=token).first()
    rf_token = RefreshToken.objects.filter(token=token_object, refresh_token=refresh_token).first()
    print(f"token:  {token},\nrefresh:  {refresh_token}")
    print(f"token:  {token_object},\nrefresh:  {rf_token}")

    if not token_object or not rf_token: # nem o token nem o refresh token existem
        return False, None, None
    
    if token_object.is_valid(): # se o token está valido o refresh token também está
        return True, token_object, rf_token

    if rf_token.is_valid(): # verifica se o refresh token está expirado(em dias) para criar outros token e refresh token
        user = token_object.user

        created, tk, rft = create_token(user)
        if not created:
            return False, None, None
        
        # Delele if token was created
        token_object.delete()
        rf_token.delete()

        return True, tk, rft
    return False, None, None

def refresh_token_v2(token: str, refresh_token: str):
        
    token_object = Token.objects.filter(token=token).first()
    rf_token = RefreshToken.objects.filter(token=token_object, refresh_token=refresh_token).first()
    print(f"token:  {token},\nrefresh:  {refresh_token}")
    print(f"token:  {token_object},\nrefresh:  {rf_token}")

    if not token_object or not rf_token: # nem o token nem o refresh token existem
        return False, None, None, 400, "Token and/or Refresh Token don't exist"
    
    if token_object.is_valid(): # se o token está valido o refresh token também está
        return True, token_object, rf_token, 200, "Tokens are valid"

    if rf_token.is_valid(): # verifica se o refresh token está expirado(em dias) para criar outros token e refresh token
        user = token_object.user

        created, tk, rft = create_token(user)
        if not created:
            return False, None, None, 500, "there was an internal error that prevented the tokens creation"
        
        # Delele if token was created
        token_object.delete()
        rf_token.delete()

        return True, tk, rft, 200, "created new token and refresh token"
    return False, None, None, 400, "Token and Refresh Token are invalid"

def encode_token(**kwargs):
    token = encode(secret, kwargs, 'HS256')
    return token


def decode_token(token):
    payload = decode(secret, token, 'HS256')
    return payload

# Validate token by request
def validate_token(request): 
    token = request.META.get('HTTP_AUTHORIZATION')
    refresh_token= request.META.get('HTTP_AUTHORIZATION')
    return validateToken(token, refresh_token)[:2]

def validate_token_v2(request): 
    token = request.META.get('HTTP_AUTHORIZATION')
    refresh_token= request.META.get('HTTP_AUTHORIZATION')
    return validateToken(token, refresh_token)


# Validate token by token and refresh token
'''
    Returns:
        - bool: A boolean to say if is authenticated or not
        - User: A reference to object owner of that token
        - str: A raise when the response is negative to validate
'''
def validateToken(token: str, refresh_token: str) -> Tuple[bool, User, str]:
    if not token:
        return False, None, "token not sent"
    try:
        token = token.split(' ')[1]  # Token apsidgnapsdngp
    except IndexError:
        return False, None, "token doesn't start with Token word"

    token_object = Token.objects.filter(token=token).order_by('-iat').first()
    if not token_object:
        return False, None, "token not found"

    is_to_refactor, _ = verify_expiration(token_object)
    if is_to_refactor:
        refresh_object = RefreshToken.objects.filter(token=token_object).first()
    
        if not refresh_object:
            return False, None, "refresh token not found"
        
        if refresh_object.token.pk != token_object.pk:
            return False, None, "refresh token is not associated with this token"
        
        if not refresh_object.is_valid():
            # Update Token
            current_time = timezone.localtime(timezone.now())
            exp_date = current_time + timedelta(days=90)
            
            # Refresh token is valid so we can amplify the time of token validation
            new_token = encode_token(email=token_object.user.email, user_id=token_object.user.pk,
                                iat=current_time.timestamp(), exp=exp_date.timestamp())
            token_object.token = new_token
            token_object.iat = current_time
            token_object.expires_at = exp_date
            token_object.save()

            exp_date = exp_date + timedelta(days=7)
            new_rft = encode_token(iat=current_time.timestamp(), exp=exp_date.timestamp())

            # Update Refresh Token
            refresh_object.refresh_token = new_rft
            refresh_object.iat = current_time
            refresh_object.expires_at = exp_date
            refresh_object.save()
        
        return True, token_object.user, ""
    
    return True, token_object.user, ""


def verify_expiration(token: Token):
    # Verificar passou de 1 dia
    when_expired = token.expires_at.timestamp()

    current_time = timezone.localtime(timezone.now())
    current = current_time.timestamp()

    if current > when_expired:
        exp_date = current_time + timedelta(days=90)

        return True, exp_date
    return False, token.expires_at


def token_required(func):
    @wraps(func)
    def decorated_function(viewset, request, *args, **kwargs):
        is_valid, user, message = validate_token_v2(request)
        if not is_valid or not user:
            return UnauthorizedRequest(message=message if message else "Invalid token.")
        request.user = user
        return func(viewset, request, *args, **kwargs)
    return decorated_function

def validate_static_token(request, valid_token: str):  # is_authenticate, Usuario
    token = request.META.get('HTTP_AUTHORIZATION')
    print(token, valid_token)
    
    if not token:
        return False
    try:
        token = token.split(' ')[1]  # Token apsidgnapsdngp
    except IndexError:
        return False

    return token == valid_token

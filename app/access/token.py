from simplejwt.jwt import encode, decode
from project.settings import SECRET_KEY as secret

# Models
from access.models import Token, RefreshToken, User

# Log
from logs.views import saveLog
from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())

# Datetime
from datetime import datetime
from datetime import timedelta
import pytz
from django.utils import timezone

# Create token after user is authenticated (login) and give more time to it
def create_token(user: User):


    current_time = timezone.localtime(timezone.now())
    token_object = Token.objects.filter(user=user).order_by('-iat').first()
    if not token_object:  # Se não existe token, cria um novo

        token_exp_date = current_time + timedelta(days=7)

        token = encode_token(email=user.email, user_id=user.pk, iat=current_time.timestamp(), exp=token_exp_date.timestamp())
        try:
            token_object = Token.objects.create(
                user=user,
                expires_at=token_exp_date,
                token=token,
                iat=current_time
            )

            # CREATE REFRESH TOKEN
            refresh_token = encode_token(iat=current_time.timestamp(), exp=token_exp_date.timestamp())
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

    rf_token = RefreshToken.objects.filter(token=token_object).order_by('-iat').first()

    if not rf_token:
        # Cria um refresh token caso não exista

        rf_token_exp_date = current_time + timedelta(7)
        refresh_token = encode_token(iat=current_time.timestamp(), exp=rf_token_exp_date.timestamp())
        
        rf_token = RefreshToken.objects.create(
            token=token_object,
            refresh_token=refresh_token,
            expires_at=rf_token_exp_date,
            iat=current_time
        )

    if not token_object.is_valid() and not rf_token.is_valid():
        # cria um novo token e refresh token se ambos estiverem expirados

        token_exp_date = current_time + timedelta(days=7)
        
        token = encode_token(email=user.email, user_id=user.pk, iat=current_time.timestamp(), exp=token_exp_date.timestamp())

        token_object.token = token  # Atualiza a string do token
        token_object.iat = current_time
        token_object.expires_at = token_exp_date
        token_object.save()

        # Atualiza o refresh token
        new_rft_exp_date = current_time + timedelta(days=7)
        new_rft = encode_token(iat=current_time.timestamp(), exp=new_rft_exp_date.timestamp())
        rf_token.refresh_token = new_rft  # Atualiza a string do refresh token
        rf_token.iat = current_time
        rf_token.expires_at = new_rft_exp_date
        rf_token.save()
    
    return True, token_object, rf_token

def refresh_token(token: str, refresh_token: str):
    token_object = Token.objects.filter(token=token).first()
    rf_token = RefreshToken.objects.filter(token=token_object, refresh_token=refresh_token).first()

    if not token_object or not rf_token:
        return False, None, None
    
    if token_object.is_valid():
        return True, token_object, rf_token

    if rf_token.is_valid():
        user = token_object.user
        token_object.delete()
        rf_token.delete()
        created, tk, rft = create_token(user)
        if not created:
            return False, None, None
        return True, tk, rft
    return False, None, None



def encode_token(**kwargs):
    token = encode(secret, kwargs, 'HS256')
    return token


def decode_token(token) -> dict:
    payload = decode(secret, token, 'HS256')
    return payload[1] if len(payload) > 1 else {}


def validate_token(request):  # is_authenticate, Usuario
    token = request.META.get('HTTP_AUTHORIZATION')
    # refresh_token= request.META.get('HTTP_AUTHORIZATION')
    
    if not token:
        return False, None
    try:
        token = token.split(' ')[1]  # Token apsidgnapsdngp
    except IndexError:
        return False, None

    token_object = Token.objects.filter(token=token).first()
    if not token_object:
        return False, None

    expired = verify_expiration(token_object)
    if expired:
        return False, token_object.user

    return True, token_object.user


# Verifica a validade do token
def verify_expiration(token: Token) -> bool:
    when_expired = token.expires_at.timestamp()

    current_time = datetime.now(tz=pytz.timezone('America/Sao_Paulo'))
    current = current_time.timestamp()

    if current > when_expired:
        return True

    return False

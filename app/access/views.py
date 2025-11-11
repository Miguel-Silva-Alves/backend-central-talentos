from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from access.models import *
from access.serializer import *
import uuid

# Validation
from passlib.hash import django_pbkdf2_sha256 as handler

# Common
from common.token import TokenValidator
from common.response import ResponseDefault, CreatedRequest, BadRequest, NotFound, UnauthorizedRequest

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @TokenValidator.require_x_api_key
    def list(self, request, *args, **kwargs):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return ResponseDefault("list of users", {"users": serializer.data})

    @TokenValidator.require_x_api_key
    def retrieve(self, request, *args, **kwargs):
        try:
            user = self.get_object()
        except Exception:
            return NotFound("user not found")
        serializer = self.get_serializer(user)
        return ResponseDefault("user retrieved", {"user": serializer.data})

    @TokenValidator.require_x_api_key
    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            password = data.get("password")

            if not password:
                return BadRequest("password is required")

            data["password"] = handler.hash(password)

            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return CreatedRequest({"user": serializer.data})

            return BadRequest(serializer.errors)

        except Exception as e:
            return BadRequest(str(e))

    @TokenValidator.require_token
    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ResponseDefault("user updated", {"user": serializer.data})
        return BadRequest(serializer.errors)

    @TokenValidator.require_token
    def destroy(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return ResponseDefault("user deleted")

    @TokenValidator.require_x_api_key
    @swagger_auto_schema(
        method='post',
        operation_description="Login com email e senha",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email', 'password']
        ),
        responses={200: TokenSerializer()}
    )
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        if not user:
            return UnauthorizedRequest('User with given email does not exist.')
        
        if not handler.verify(password, user.password):
            return UnauthorizedRequest("Invalid password.")
        
        # Find some token
        token_user = Token.objects.filter(user=user).first()
        if token_user and token_user.is_valid():
            return ResponseDefault(data = TokenSerializer(token_user).data)

        token = Token.objects.create(
            token=str(uuid.uuid4()),
            user=user
        )

        return ResponseDefault(data = TokenSerializer(token).data)

    @TokenValidator.require_x_api_key
    @swagger_auto_schema(
        method='post',
        operation_description="Login via Google (com client_id e sid)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'client_id': openapi.Schema(type=openapi.TYPE_STRING),
                'sid': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email', 'client_id', 'sid']
        ),
        responses={200: TokenSerializer()}
    )
    @action(detail=False, methods=['post'], url_path='login/google')
    def login_google(self, request):
        email = request.data.get('email')
        client_id = request.data.get('client_id')
        sid = request.data.get('sid')

        try:
            google_auth = GoogleAuthentication.objects.get(sid=sid)
            user = google_auth.user

        except GoogleAuthentication.DoesNotExist:
            # ✅ Criar novo usuário
            user = User.objects.create(
                username=email.split("@")[0],
                email=email
            )

            google_auth = GoogleAuthentication.objects.create(
                sid=sid,
                email=email,
                user=user,  # ✅ AGORA TEM USER!
            )

        user, _ = User.objects.get_or_create(email=email)

        token = Token.objects.create(
            token=str(uuid.uuid4()),
            iat=timezone.now(),
            expires_at=timezone.now() + timezone.timedelta(hours=1),
            user=user
        )

        return Response(TokenSerializer(token).data, status=status.HTTP_200_OK)

    @TokenValidator.require_x_api_key
    @swagger_auto_schema(
        method='post',
        operation_description="Solicitar código de recuperação de senha",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email']
        ),
        responses={200: 'Código enviado'}
    )
    @action(detail=False, methods=['post'], url_path='password/request')
    def request_password_reset(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Usuário não encontrado.'}, status=404)

        code = str(uuid.uuid4())[:8]
        RecoveryPassword.objects.create(user=user, code=code, is_active=True)

        # Aqui você pode enviar o código por e-mail
        return Response({'detail': f'Código de recuperação gerado: {code}'}, status=200)

    @TokenValidator.require_x_api_key
    @swagger_auto_schema(
        method='post',
        operation_description="Alterar senha com código de recuperação",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'code': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email', 'code', 'new_password']
        ),
        responses={200: 'Senha alterada com sucesso'}
    )
    @action(detail=False, methods=['post'], url_path='password/reset')
    def reset_password(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')

        try:
            user = User.objects.get(email=email)
            recovery = RecoveryPassword.objects.filter(user=user, code=code, is_active=True).last()
            if not recovery or not recovery.is_valid():
                return Response({'detail': 'Código inválido ou expirado.'}, status=400)
        except User.DoesNotExist:
            return Response({'detail': 'Usuário não encontrado.'}, status=404)

        user.set_password(new_password)
        user.save()
        recovery.invalidate()

        return Response({'detail': 'Senha alterada com sucesso.'}, status=200)

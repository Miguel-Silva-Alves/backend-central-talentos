from access.models import User, EmailPasswordAuthentication, GoogleAuthentication
from django.utils import timezone

# RestFramework
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

# Swagger
from drf_yasg.utils import swagger_auto_schema

#Responses
from common.response import ResponseDefault, BadRequest, UnauthorizedRequest, CreatedRequest, InternalError, ForbiddenRequest
from common.token import refresh_token
from access.responses import CreateUserResponse, LoginResponse, RefreshResponse

# Validation
from passlib.hash import django_pbkdf2_sha256 as handler

# Logs
from logs.views import saveLog

# Code and Verify
from common.response import ResponseDefault, BadRequest

# Token
from access.token import create_token

#Serializer 
from access.serializer import RegisterUserForm, RegisterLoginForm, RefreshTokenSerializer


class RegisterUser(ViewSet):
    serializer_class = RegisterUserForm
    queryset = User.objects.all()

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = []
        if self.action == 'password':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
      
    @swagger_auto_schema(request_body=RegisterUserForm, responses=CreateUserResponse, operation_description="Creates an user in the database.")
    def create(self, request, *args, **kwargs):
        serializer = RegisterUserForm(data=request.data)
        
    
        return CreatedRequest(data={
        })

    def _loginGoogle(self, email, client_id, photo):
        user = User.objects.filter(email=email).first()
        if not user:
            return UnauthorizedRequest("User not Found")
        
        # # Verifica se o estudante existe e se ele aceitou os termos
        # student = Student.objects.filter(user=user).first()
        # if student and not student.student_accepted_term:
        #     return ForbiddenRequest(message="The student has not accepted the terms")

        # # Verifica se existe uma anamnese para o estudante
        # anamnese_exists = Anamnese.objects.filter(student=student).exists()
        # if not anamnese_exists:
        #     return ...

        # # Verifica se a autenticação do Google já existe para o usuário
        # exist = GoogleAuthentication.objects.filter(
        #     user=user,
        #     email=email,
        #     client_id=client_id,
        # ).exists()

        # if exist:
        #     # Gera e retorna o token, pois o usuário já possui autenticação configurada
        #     token_has_created, token, rf_token = create_token(user)
        #     if not token_has_created:
        #         return BadRequest("Token not created")
            
        #     return ResponseDefault(data={
        #         'username': user.username,
        #         'user_id': user.pk,
        #         'student_id': student.pk,
        #         'is_staff': user.is_staff,
        #         'anamnese': anamnese_exists,
        #         'token': token.token,
        #         'refresh_token': rf_token.refresh_token
        #     })
        
        # # Cria uma nova autenticação do Google para o usuário
        # GoogleAuthentication.objects.create(
        #     user=user,
        #     email=email,
        #     client_id=client_id,
        # )

        # # Atualiza a foto do estudante e o horário do último login do usuário
        # student.photo = photo
        # student.save()
        # user.last_login = timezone.now()
        # user.save(update_fields=['last_login'])

        # # Gera e retorna o token
        # token_has_created, token, rf_token = create_token(user)
        # if not token_has_created:
        #     return BadRequest("Token not created")
        
        # return ResponseDefault(data={
        #     'username': user.username,
        #     'user_id': user.pk,
        #     'student_id': student.pk,
        #     'is_staff': user.is_staff,
        #     'anamnese': anamnese_exists,
        #     'token': token.token,
        #     'refresh_token': rf_token.refresh_token
        # })
        return ResponseDefault({})


    @swagger_auto_schema(request_body=RegisterLoginForm, responses=LoginResponse)
    @action(detail=False, methods=['POST'], name='Login')
    def login(self, request):
        # serializer = RegisterLoginForm(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # email = request.data.get('email', None)
        # password = request.data.get('password', None)
        # client_id = request.data.get('client_id', None)
        # photo = request.data.get('photo', "")
        
        # if client_id:
        #    #login com google
        #    return self._loginGoogle(email, client_id, photo)
        
        # user = User.objects.filter(email=email).first()
        # if user is None:
        #     return UnauthorizedRequest(message="Invalid email or password")

        # student = Student.objects.filter(user=user).first()
        # if student and not student.student_accepted_term:
        #     return ForbiddenRequest(message="The student has not accepted the terms")
        # anamnese_exists = Anamnese.objects.filter(student=student).exists()
        # try:                        
        #     if password:
        #         auth_entry = EmailPasswordAuthentication.objects.filter(user=user).first()
        #         if not auth_entry or not handler.verify(password, auth_entry.password):
        #             return BadRequest(message="Invalid email or password")
                
        #         token_has_created, token, rf_token = create_token(user)
        #         if not token_has_created:
        #             return BadRequest("Token not created")
                        
        #     user.last_login = timezone.now()
        #     user.save(update_fields=['last_login'])
            
        #     return ResponseDefault(data={
        #         'username': user.username,
        #         'user_id': user.pk,
        #         'student_id': student.pk,
        #         'is_staff': user.is_staff,
        #         'anamnese' : anamnese_exists,
        #         'token': token.token,
        #         'refresh_token': rf_token.refresh_token
        #     })
        # except Exception as e:
        #     saveLog(msg=f'Login fails because {e}', type='Error', path="access/views.py line 234")
        #     return InternalError(str(e))
        return ResponseDefault()

        
    @swagger_auto_schema(request_body=RefreshTokenSerializer, operation_description="Creates another token and refresh token if the refresh token is expirated.", responses=RefreshResponse)
    @action(detail=False, methods=['POST'], name='RefreshToken')
    def refresh(self,request):
        
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = request.data.get('token')
        rf_token = request.data.get('refresh_token')

        valid, tk , rft = refresh_token(token, rf_token)
        if not valid:
            return BadRequest('Token or Refresh Token is not valid, please login again')
        
        return ResponseDefault(data={'token': tk.token, 'refresh_token':rft.refresh_token})
        
    
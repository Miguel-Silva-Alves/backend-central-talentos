# access/factories.py
import factory
from django.contrib.auth.hashers import make_password
from .models import User, Token, GoogleAuthentication, RecoveryPassword

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    password = factory.LazyFunction(lambda: make_password('testpassword123'))
    
class TokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Token
        
    user = factory.SubFactory(UserFactory)
    token = factory.Faker('uuid4')
    
class GoogleAuthenticationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GoogleAuthentication
        
    email = factory.Sequence(lambda n: f'google_user{n}@example.com')
    client_id = factory.Faker('uuid4')
    sid = factory.Faker('uuid4')
    user = factory.SubFactory(UserFactory)
    
class RecoveryPasswordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RecoveryPassword
    
    user = factory.SubFactory(UserFactory)
    code = factory.Faker('bothify', text='########') # 8 characters
    is_active = True
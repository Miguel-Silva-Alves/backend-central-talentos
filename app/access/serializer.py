from rest_framework import serializers
from password_strength import PasswordPolicy
import re
from access.models import User

# simple serializer for User
class RegisterUserForm(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField()
    password = serializers.CharField(required=False)
    client_id = serializers.CharField(required=False)
    phone = serializers.CharField()
    gender = serializers.ChoiceField(required=False, choices=["MALE", "FEMALE", "OTHER"])
    birth_date = serializers.DateField(required=False)
    objective = serializers.ListField(required=False, child=serializers.CharField())
    code = serializers.CharField(required=True)

    def valid_password(self, password):

        policy = PasswordPolicy.from_names(
            length=8,  # min length: 8
            uppercase=1,  # need min. 2 uppercase letters
            numbers=1,  # need min. 2 digits
            special=1,  # need min. 2 special characters
        )
        result = policy.test(password)
        if len(result) == 0:
            return True, None
        return False, result
    
    def validate_password(self, value, **kwargs):

        errors = kwargs.get('errors', [])
    
        val, returned = self.valid_password(value)
        if not val:
          errors.append(f'The password needs {str(returned)}')

        if len(errors) > 0:
            print(errors)
            raise serializers.ValidationError(errors)
        return value

    # def validate_email(self, value, **kwargs):
    #     errors = kwargs.get('errors', [])

    #     if User.objects.filter(email=value).exists():
    #         raise serializers.ValidationError("Email already in use")
        
    #     try:
    #         emailinfo = validEmail(value, check_deliverability=True)
    #         value = emailinfo.normalized

    #     except EmailNotValidError as err:
    #         errors.append(str(err))
    #     if len(errors) > 0:
    #         print(errors)
    #         raise serializers.ValidationError(errors)
    #     return value
    
    # def validate_name(self, value):
    #     errors = []
    #     if not re.match("^[a-zA-ZÀ-ÿ ]+$", value):
    #         errors.append("The name must contain only letters and spaces.")
    #     if len(errors) > 0:
    #         print(errors)
    #         raise serializers.ValidationError(errors)
    #     return value

    # Check if phone is just number
    def validate_phone(self, value):
        print('validate phone')
        # Define o padrão para validar números no formato (DDD XXXXX-XXXX)
        phone_regex = r'^(\+55 )?\d{2,3} ?\d{5}-?\d{4}$'
        if not re.match(phone_regex, value):
            raise serializers.ValidationError(
                "O número de telefone deve seguir o padrão (DDD XXXXX-XXXX)"
            )
        return value
    
    def validate(self, data):
        password = data.get('password')
        client_id = data.get('client_id')

        if not (password or client_id):
            raise serializers.ValidationError("At least one authentication method must be provided.")     
        return data
    
    
# simple serializer for Login
class RegisterLoginForm(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    version = serializers.CharField(required=False)
class RefreshTokenSerializer(serializers.Serializer):
    token= serializers.CharField()
    refresh_token= serializers.CharField()

class LoginTokenSerializer(serializers.Serializer):
    token= serializers.CharField()
    refresh_token= serializers.CharField()
    version = serializers.CharField(required=False)

class LoginGoogleSerializer(serializers.Serializer):
    email = serializers.EmailField()
    client_id = serializers.CharField(required=False)
    version = serializers.CharField(required=False)
    
    def validate_client_id(self, value):
        if value is None or value == '':
            raise serializers.ValidationError("This field cannot be null or empty.")
        if len(value) < 1:
            raise serializers.ValidationError("Ensure this field has at least 1 character.")
        return value

class CreatePasswordRecoveryRequest(serializers.Serializer):
    email = serializers.CharField(min_length=1)

class PasswordRecoveryRequestValidateSerializer(serializers.Serializer):
    code = serializers.CharField()

class UserChangePassword(serializers.Serializer):
    newpassword = serializers.CharField(help_text="User's new password.")
    user = serializers.EmailField(help_text="Email of the user whose password is going to be changed.")
    code = serializers.CharField(help_text="Code of the recovery password request.")

class SmartwatchSerializer(serializers.Serializer):
    id_android = serializers.CharField()
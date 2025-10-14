from password_strength import PasswordPolicy

def validate_password(password):
        '''
        Function to validate password, minimal values predefined 
        '''

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
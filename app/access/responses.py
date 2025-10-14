from drf_yasg import openapi

CreateUserResponse = {
    "201": openapi.Response(
        description="user and student created successfully.",
        examples={
            "application/json": {
                "username": "string",
                "user_id": "integer",
                "student_id": "integer", 
                "is_staff": "boolean", 
                'token': "string", 
                "refresh_token": "string", 
                "message": "created"
            }
        },
    ),
    "400": openapi.Response(
        description="""
        errors:
        * email not sent: attribute "email" wasn't sent.
        * name not sent: attribute "name" wasn't sent.
        * phone not sent: attribute "phone" wasn't sent.
        * date in invalid format: attribute "birth_date was sent in the wrong format (the correct format is YYYY-MM-DD).
        * gender is not a valid choice: the value of the attribute "gender" sent in the request is neither "MALE" or "FEMALE", which are the valid choices.
        * invalid code: there is no gym network with the sent code.
        * email not unique: there is already a user registered with the sent email.
        * no authentication method: no authentication method was provided to be linked to the user (neither of the attributes "password" or "client_id" were sent). 
        * password not valid: The password doesn't have the minimum number of characters (8), uppercase letters (1), digits (1), and special characters (1).
        * password not valid: The password doesn't have the minimum number of characters (8).
        * password not valid: The password doesn't have the minimum number of uppercase letters (1).
        * password not valid: The password doesn't have the minimum number of digits (1).
        * password not valid: The password doesn't have the minimum number of special characters (1).
        """,
        examples={
            "application/json": [
                {
                    "email": [
                        "This field is required."
                    ],
                },
                 {
                    "name": [
                        "This field is required."
                    ],
                }, {
                    "phone": [
                        "This field is required."
                    ],
                },
                {
                    "birth_date": [
                        "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
                    ]
                },
                {
                     "gender": [
                        "\"input_sent_in_the_request\" is not a valid choice."
                    ]
                },
                {
                    "message": "Gym Networking not found"
                },
                {
                    "message": "email is already in use"
                },
                {
                    "non_field_errors": ["At least one authentication method must be provided."]
                },
                {
                    "password": "The password needs [Length(8), Uppercase(1), Numbers(1), Special(1)]"
                },
                {
                    "password": "The password needs [Length(8)]"
                },
                {
                    "password": "The password needs [Uppercase(1)]"
                },
                {
                    "password": "The password needs [Numbers(1)]"
                },
                {
                    "password": "The password needs [Special(1)]"
                }
            ]
        },  
    ),
    "500": openapi.Response(
        description="An exception ocurred in the server side during the user creation.",
        examples={
            "application/json": {
                "message": "Exception"
            }
        }
    )
}

DeleteUserResponse = {
    "200": openapi.Response(
        description="Delete successful.",
        examples={
            "application/json": {
                "username": "Cauê", 
                "message": "deleted"
            }
        },
    ),
}

LoginResponse = {
    "200": openapi.Response(
        description="login successful.",
        examples={
            "application/json": {
                "user" : {
                    "email" : "string",
                    "username": "string",
                    "id": "integer",
                    "is_staff": "bool",
                },
                "student" : {
                    "id": "integer",
                    "photo" : "string",
                    "anamnese": "bool",
                },
                "gym": {
                    "name": "string",
                    "photo": "string",
                    "networking": "string",
                },
                "token": "string",
                "refresh_token": "string",
                "message": "ok",
            }
        }
    ),
    "401": openapi.Response(
        description="""
        errors:
        * user not found: user with the email specified doesn't exist.
        """,
        examples={
            "application/json": [
                {
                    "message": "Invalid email or password"
                },
            ]
        },
    ),
    "403": openapi.Response(
        description="""
        errors:
        * Student has not accepted the terms: User has not accepted the terms on the app.
        * No gym linked to the student: User needs find some academy by location and set this to the system.
        """,
        examples={
            "application/json": [
                {
                    "token": "string",
                    "refresh_token": "string",
                    "error_code": 1,
                    "gym": {
                        "name": "string",
                        "photo": "string",
                        "networking": "string"
                    },
                    "message": "The student has not accepted the terms",
                },
                {
                    "token": "string",
                    "refresh_token": "string",
                    "error_code": 2,
                    "message": "no gym linked to the student"
                }
            ]
        },
    ),
    "400": openapi.Response(
        description="""
        errors:
        * invalid password: user with the email specified doesn't have this password.
        * token not created: there was an error in the server side that prevented the token creation.
        """,
        examples={
            "application/json": [
                {
                    "bad_request": True,
                    "message": "Invalid email or password",
                    "detail": "auth_entry: bool, handler.verify: bool",

                },
                {
                    "bad_request": True,
                    "message": "Token not created",
                    "detail": "No token found" 
                },
            ]
        },  
    ),
    "500": openapi.Response(
        description="An exception ocurred in the server side during the login.",
        examples={
            "application/json": {
                "message": "Exception"
            }
        }
    )
}

LoginGoogleResponse = {
    "200": openapi.Response(
        description="login successful.",
        examples={
            "application/json": {
                "user" : {
                    "email" : "string",
                    "username": "string",
                    "id": "integer",
                    "is_staff": "bool",
                },
                "student" : {
                    "id": "integer",
                    "photo" : "string",
                    "anamnese": "bool",
                },
                "gym": {
                    "name": "string",
                    "photo": "string",
                    "networking": "string",
                },
                "token": "string",
                "refresh_token": "string",
                "message": "ok",
            }
        }
    ),
    "401": openapi.Response(
        description="""
        errors:
        * user not found: user with the email specified doesn't exist.
        * wrong client id: sent client id is not the client id that is linked to the google account of the user in the system.
        """,
        examples={
            "application/json": [
                {
                    "message": "user not found"
                },
                {
                    "message": "wrong client id"
                }
            ]
        },
    ),
    "403": openapi.Response(
        description="""
        errors:
        * Student has not accepted the terms: User has not accepted the terms on the app.
        * No gym linked to the student: User needs find some academy by location and set this to the system.
        """,
        examples={
            "application/json": [
                {
                    "message": "The student has not accepted the terms",
                    "token": "string",
                    "refresh_token": "string",
                    "error_code": 1,
                    "gym": {
                        "name": "string",
                        "photo": "string",
                        "networking": "string"
                    }
                },
                {  
                    "message": "no gym linked to the student",
                    "token": "string",
                    "refresh_token": "string",
                    "error_code": 2
                }
            ]
        },
    ),
    "400": openapi.Response(
        description="""
        errors:
        * token not created: there was an error in the server side that prevented the token creation.
        """,
        examples={
            "application/json": [
                {
                    "message": "Token not created" 
                },
            ]
        },  
    ),
    "500": openapi.Response(
        description="An exception ocurred in the server side during the login.",
        examples={
            "application/json": {
                "message": "Exception"
            }
        }
    )
}

LoginTokenResponse = {
    "200": openapi.Response(
        description="login successful.",
        examples={
            "application/json": {
                "user" : {
                    "email": "string",
                    "username": "string",
                    "id": "integer",
                    "is_staff": "bool",
                },
                'student' : {
                    "id": "integer",
                    "photo" : "string",
                    "anamnese": "bool",
                },
                "gym": {
                    "name": "string",
                    "photo": "string",
                    "networking": "string",
                },
                "token": "string",
                "refresh_token": "string"
            }
        },
    ),
    "401": openapi.Response(
        description="""
        errors:
        * Token not sent: Token was not sent.
        * Token with invalid format: Sent token doesn't follow the valid format 'Token token'.
        * Token not found: There is no token associated to this user.
        * Refresh Token not found: There is no refresh token to this user.
        * Refresh Token is not associated with the sent token.
        * Invalid Refresh Token: Refresh token is expirated.
        * Token not created: There was a problem during the token creation if the token needs to be refactored.
        * Student not found: The user doesn't have any student associated to them.
        """,
        examples={
            "application/json": [
                {
                    "message": "token not sent"
                },
                {
                    "message": "token doesn't start with Token word"
                },
                {
                    "message": "token not found"
                },
                {
                    "message": "refresh token not found",
                },
                {
                    "message": "refresh token is not associated with this token",
                },
                {
                    "message": "refresh token is invalid",
                },
                {
                    "message": "token not created",
                },
                {
                    "message": "Student not found",
                }
            ]
        },
    ),
    "403": openapi.Response(
        description="""
        errors:
        * No gym linked to the student: User needs find some academy by location and set this to the system.
        * Student has not accepted the terms: User has not accepted the terms on the app.
        """,
        examples={
            "application/json": [
                {
                    "token": "string", 
                    "refresh_token": "string",
                    "error_code": 2,
                    "message": "no gym linked to the student" , 
                },
                {   
                    "message": "student has not accepted the terms",        
                    "token": "string", 
                    "refresh_token": "string",
                    "error_code": 1,
                    'gym': {
                        'name' : "string",
                        'photo' : "string",
                        'networking' : "string",
                    }
                },
            ]
        },
    ),
}

RecoveryPasswordRequestResponse = {
    "200": openapi.Response(
        description="Password recovery request created successfully.",
        examples={
            "application/json": {
                "message": "Email sent with the link to recover the password"
            }
        }
    ),
    "401": openapi.Response(
        description="""
        errors:
        * Email not found: A user with the email specified wasn't found.
        * Phone not found: A student with the phone specified wasn't found, and therefore no user was found.
        """,
        examples={
            "application/json": {
                "message":  "user not found with email or phone specified"
            }
        }
    ),
    "500": openapi.Response(
        description="""
        errors:
        * Error generating the code: There was an error in the server side that prevented the password recovery request creation.
        """,
        examples={
            "application/json": [
                {
                    "message": "Exception" 
                },
            ]
        },
    ),
}

RecoveryPasswordResponse = {
    "200": openapi.Response(
        description="Password changed successfully.",
        examples={
            "application/json": {
                "message": "changed"
            }
        },
    ),
    "400": openapi.Response(
        description="""
        errors:
        * Password not valid: The password must have at minimum: 8 characters, 1 uppercase letter, 1 digit, and 1 special character.
        """,
        examples={
            "application/json": [
                {
                    "message": "the new password needs [Length(8), Uppercase(1), Special(1)]"
                },
            ]
        },
    ),
    "401": openapi.Response(
        description="""
        errors:
        * Recovery Password Request Not Found: There isn't a password recovery request for this user with the code specificated.
        * Recovery Password Request Invalid: The password recovery request is not valid anymore (it is expirated and inactive).
        """,
        examples={
            "application/json":
                {
                    "message": "not allowed" 
                },
        },
    ),
    "500": openapi.Response(
        description="An error ocurred in the server side during the password change.",
        examples={
            "application/json":
                {
                    "message": "Exception"
                }
        }
    )
}

DisableAccountResponse = {
    "200": openapi.Response(
        description="User account disabled successfully.",
        examples={
            "application/json":
                {
                    "message": "account disabled"
                }
        }
    ),
     "403": openapi.Response(
        description= "Application Not Allowed: Api Key of the application is not specified in the request header or the application doesn't exist.",
        examples={
            "application/json":
                {
                    "message": "Application not allowed" 
                }
        },
    ),
}

DisableApplicationResponse = {
    "200": openapi.Response(
        description="Application disabled successfully.",
        examples={
            "application/json": {
                "message": "application disabled"
            }
        }
    ),
    "400": openapi.Response(
        description="User not found.",
        examples={
            "application/json": {
                "message": "user not found"
            }
        }
    ),
     "403": openapi.Response(
        description= "Application Not Allowed: Api Key of the application is not specified in the request header or the application doesn't exist.",
        examples={
            "application/json":
                {
                    "message": "Application not allowed" 
                }
        },
    ),
}

RemoveUserResponse = {
    "200": openapi.Response(
        description="User successfully removed.",
        examples={
            "application/json": {
                "message": "Account successfully removed."
            }
        }
    ),
    "500": openapi.Response(
        description="Error in the server side.",
    ),
}

LinkAccountResponse = {
    "200": openapi.Response(
        description="Auth account linked to google account successfully.",
        examples={
            "application/json": {
                "message": "linked account"
            }
        }
    ),
    "401": openapi.Response(
        description="""
        errors:
        * Token not present: "Authorization" header with token is not set.
        * Tokin Invalid: The token is not valid anymore (it is expirated).
        """,
        examples={
            "application/json": [
                {
                    "message": "Token not Found" 
                },
                {
                    "message": {
                        "error": "token not available"
                    }
                }
            ]
        },
    ),
}

ReactivateApplicationResponse = {
    "200": openapi.Response(
        description="Application was re-added successfully to the user.",
        examples={
            "application/json": {
                "message": "application reactivate"
            }
        }
    ),
    "400": openapi.Response(
        description="User with the email specified in the request was not found.",
        examples={
            "application/json": {
                "message": "user not found"
            }
        }
    ),
    "403": openapi.Response(
        description= "Application Not Allowed: Api Key of the application is not specified in the request header or the application doesn't exist.",
        examples={
            "application/json":
                {
                    "message": "Application not allowed" 
                }
        },
    ),
}

ResendCodeResponse = {
    "200": openapi.Response(
        description="New password recovery request created successfully.",
        examples={
            "application/json": {
                "message": "ok"
            }
        }
    ),
    "400": openapi.Response(
        description="""
        errors:
        * Password Recovery Request not found: A password recovery request with the code specified was not found.
        * Error generating the code: There was an error in the server side that prevented the password recovery request creation.
        """,
        examples={
            "application/json": [
                {
                    "message": "password recovery request with specified code was not found" 
                },
                {
                    "message": "There was an error while trying to generate a code"
                },
            ]
        },
    ),
}

RefreshResponse = {
    "200": openapi.Response(
        description="New token and refresh token created.",
        examples={
            "application/json": {
                'token': "string", 
                "refresh_token": "string",
                "message": "ok"
            }
        }
    ),
    "400": openapi.Response(
        description="""
        errors:
        * Token(s) doesn't exist: One of the tokens or all the tokens don't exist.
        * Tokens invalid: The token and refresh token aren't valid anymore (they're expirated).
        """,
        examples={
            "application/json": [
                {
                    "message": "Token and/or Refresh Token don't exist"
                },
                {
                    "message": "Token and Refresh Token are invalid"
                },
            ]
        }
    ),
    "500": openapi.Response(
        description="""
        errors:
        * Tokens not created: There was a problem in the server side that prevented the tokens creation.
        """,
        examples={
            "application/json": {
                "message": "Exception"
            }
        }
    )
}

ValidatePasswordRecoveryRequest = {
    "200": openapi.Response(
        description="Password Recovery Request is valid and it is not expirated.",
        examples={
            "application/json": {
                "message": "ok"
            }
        }
    ),
    "400": openapi.Response(
        description="""
        errors:
        * Password Recovery Request inexistent: A password recovery request with the code specified doesn't exist.
        * Password Recovery Request expirated: The request is already expirated.
        """,
        examples={
            "application/json": [
                {
                    "message": "invalid or incorret code"
                },
                {
                    "message": "timeout, token expired"
                }
            ]
        },
    ),
}

ValidateTokenResponse = {
    "200": openapi.Response(
        description="The token is valid.",
        examples={
            "application/json": {
                "email": "caue@email.com",
                "is_staff": True, 
                "username": "Cauê",
                "message": "ok"
            }
        }
    ),
    "400": openapi.Response(
        description="The user associated with the token doesn't exist.",
        examples={
            "application/json": 
                {
                    "message": "user not found"
                },
        },
    ),
    "401": openapi.Response(
        description="""
        errors:
        * Token inexistent: Token doesn't exist.
        * Token Invalid: The token is not valid anymore (it is expirated).
        """,
        examples={
            "application/json": [
                {
                    "message": "token not Found" 
                },
                {
                    "message": {
                        "error": "token not available"
                    }
                }
            ]
        }),
}

GetToLinkResponse = {
    "200": openapi.Response(
        description="The account can be linked with the google account.",
        examples={
            "application/json":
            {
                "message": True
            }
        }
    ),
    "400": openapi.Response(
        description="The user associated with the token doesn't exist.",
        examples={
            "application/json": 
                {
                    "message": "email not found"
                },
        },
    ),
    "401": openapi.Response(
        description="""
        errors:
        * Token not present: Authorization header with token wasn't sent.
        * Token inexistent: Token doesn't exist.
        * Token Invalid: The token is not valid anymore (it is expirated).
        """,
        examples={
            "application/json": [
                {
                    "message": "token not Found" 
                },
                {
                    "message": {
                        "error": "token not available"
                    }
                }
            ]
        }),
}

ValidatePasswordRecoveryRequest = {""
    "200": openapi.Response(
        description="Password Recovery Request is valid and it is not expirated.",
        examples={
            "application/json": {
                "message": "valid code"
            }
        }
    ),
    "400": openapi.Response(
        description="""
        errors:
        * Password Recovery Request inexistent: A password recovery request with the code specified doesn't exist.
        * Password Recovery Request expirated: The request is already expirated.
        """,
        examples={
            "application/json": [
                {
                    "message": "password recovery request with specified code was not found"
                },
                {
                    "message": "timeout, token expired"
                }
            ]
        },
    ),
}

DeleteUserResponse = {
    "200": openapi.Response(
        description="Delete successful.",
        examples={
            "application/json": {
                "message": "User deleted successfully"
            }
        },
    ),
    "500": openapi.Response(
        description="An internal error occurred during the user deletion.",
        examples={
            "application/json": {
                "message": "Exception"
            }
        }
    )
}

GenerateCodeToValidateEmailResponse = {
    "200": openapi.Response(
        description="Code to validate email was successfully generated and sent to the specified email.",
        examples={
            "application/json": {
                "message": "Validation code sent to email."
            }
        }
    ),
    "400": openapi.Response(
        description="""
        Errors:
        * Parameter 'email' wasn't sent in the request body.
        * Email sent isn't in a valid email format.
        """,
        examples={
            "application/json": [
                {
                    "email": [
                        "This field is required."
                    ]
                },
                {
                    "email": [
                        "Enter a valid email address."
                    ]
                }
                
            ], 
        },
    ),
    "500": openapi.Response(
        description="Internal Error in back-end.",
        examples={
            "application/json": [
                {
                    "message": "There was an error while trying to generate a code: <exception>"
                },
            ]
        },
    ),
}

ValidateEmailCodeResponse = {
    "200": openapi.Response(
        description="Code to validate email was successfully verified (it can be valid or not).",
        examples={
            "application/json": {
                "is_valid": "bool",
                "message": "ok"
            }
        }
    ),
    "400": openapi.Response(
        description="""
        Errors:
        * Parameter 'email' wasn't sent in the request body.
        * Parameter 'code' wasn't sent in the request body.
        * Parameter 'email' and 'code' weren't sent in the request body.
        * Email sent isn't in a valid email format.
        * Code isn't a six digit code.
        """,
        examples={
            "application/json": [
                {
                    "email": [
                        "This field is required."
                    ],
                },
                {
                    "code": [
                        "This field is required."
                    ],
                },
                {
                    "email": [
                        "This field is required."
                    ],
                    "code": [
                        "This field is required."
                    ],
                },
                {
                    "email": [
                        "Enter a valid email address."
                    ]
                },
                {
                    "code": [
                        "Ensure this field has at least 6 characters."
                    ]
                },
                {
                    "code": [
                        "Ensure this field has no more than 6 characters."
                    ]
                }]
        },
    ),
    "404": openapi.Response(
        description="Code sent in the request body isn't linked to the email sent in the request body.",
        examples={
            "application/json": {
                "message": "This code isn't linked to this email."
            }
        }
    )
}
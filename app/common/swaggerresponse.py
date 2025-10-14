from drf_yasg import openapi

def setResponse200(name):
    return openapi.Response(
        description="custom 200 description",
        examples={
            "application/json": {
                name: [],
                "message": "ok"
            }
        }
    ),

possibilities = {
    "201": openapi.Response(
        description="custom 201 description",
        examples={
            "application/json": {
                "message": "created"
            }
        }
    ),
    "202": openapi.Response(
        description="custom 202 description",
        examples={
            "application/json": {
                "message": "accepted"
            }
        }
    ),
    "204": openapi.Response(
        description="custom 204 description",
        examples={
            "application/json": {
                "message": "not found"
            }
        }
    ),
    "401": openapi.Response(
        description="custom 401 description",
        examples={
            "application/json": {
                "detail": "Invalid token."
            }
        }
    ),
    "400": openapi.Response(
        description="custom 400 description",
        examples={
            "application/json": {
                "message": "abstence of parameters"
            }
        }
    ),
    "500": openapi.Response(
        description="custom 500 description",
        examples={
            "application/json": {
                "message": "INTERNAL ERROR"
            }
        }
    ),
}
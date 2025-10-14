from rest_framework.response import Response
from rest_framework import status


def BadRequest(message='error', **kwargs):
    data={'message': message}
    for key in kwargs.items():
        if key[0] not in data:
            data[key[0]] = key[1]
    return Response(status=status.HTTP_400_BAD_REQUEST, data=data)

def InternalError(error='error'):
    return Response(data={'message': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def CreatedRequest(message = "created", data = {}):
    data['message'] = message
    return Response(data=data, status=status.HTTP_201_CREATED)

def ResponseDefault(message='ok', data={}):
    data['message'] = message
    return Response(status=status.HTTP_200_OK, data=data)

def NotFound(message='not found', data={}):
    data['message'] = message
    return Response(status=status.HTTP_404_NOT_FOUND, data=data)

def ChangeRequest(message = 'changed'):
    return Response(data={'message': message}, status=status.HTTP_200_OK)

def UnauthorizedRequest(message = "not allowed", **kwargs):
    data = {'message': message}
    for key in kwargs.items():
        if key[0] not in data:
            data[key[0]] = key[1]
    return Response(status=status.HTTP_401_UNAUTHORIZED, data=data)

def AcceptedRequest():
    return Response(status=status.HTTP_202_ACCEPTED,data={'message': 'accepted'})

def NotAcceptedRequest(data={}, message='not accepted'):
    data['message']= message
    return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)

def ForbiddenRequest(data:dict ={}, message='Forbidden', **kwargs):
    data['message'] = message
    for key in kwargs.items():
        if key[0] not in data:
            data[key[0]] = key[1]
    return Response(data=data, status=status.HTTP_403_FORBIDDEN)
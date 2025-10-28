from rest_framework import viewsets
from rest_framework.decorators import action

from ai.models import Queries
from ai.serializer import QuerieSerializer

# Swagger
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Common
from common.token import TokenValidator
from common.response import ResponseDefault, BadRequest


class QuerieViewSet(viewsets.ModelViewSet):
    queryset = Queries.objects.all()
    serializer_class = QuerieSerializer

    # @swagger_auto_schema(
    #     method='post',
    #     operation_description="Faz uma query única e processa suas informações.",
    #     manual_parameters=[
    #         openapi.Parameter(
    #             'prompt',
    #             openapi.IN_FORM,
    #             description="String da query a ser enviada",
    #             type=openapi.TYPE_STRING,
    #             required=True
    #         )
    #     ],
    #     responses={200: openapi.Response('Query concluída')}
    # )
    @action(detail=False, methods=['post'], url_path='prompt')
    @TokenValidator.require_token
    def prompt(self, request):
        # Verifica se veio uma prompt
        prompt_text = request.data.get('prompt')
        if not prompt_text:
            return BadRequest("Nenhum prompt enviado.")

        return ResponseDefault(
            message="Query processed",
            data={
                "query": prompt_text,
            }
        )

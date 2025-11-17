from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rh.models import File
from rh.serializer import FileSerializer

from common.token import TokenValidator
from common.response import ResponseDefault, NotFound, UnauthorizedRequest

import os


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]  # TokenValidator já controla

    # ----------------------
    #      RETRIEVE
    # ----------------------
    @TokenValidator.require_token
    def retrieve(self, request, *args, **kwargs):
        try:
            file = self.get_object()
        except Exception:
            return NotFound("file not found")

        serializer = self.get_serializer(file)

        return ResponseDefault(
            "file retrieved",
            {"file": serializer.data}
        )

    # ----------------------
    #       UPLOAD
    # ----------------------
    @swagger_auto_schema(
        method='post',
        operation_description="Upload de arquivo e processamento.",
        manual_parameters=[
            openapi.Parameter(
                "file",
                openapi.IN_FORM,
                description="Arquivo a ser enviado",
                type=openapi.TYPE_FILE,
                required=True,
            )
        ],
        responses={200: openapi.Response("Upload concluído")}
    )
    @action(detail=False, methods=["post"], url_path="upload")
    @TokenValidator.require_token
    def upload(self, request):
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return UnauthorizedRequest("Nenhum arquivo enviado.")

        file_name = uploaded_file.name
        file_size_mb = round(uploaded_file.size / (1024 * 1024), 2)

        # cria registro
        file_obj = File.objects.create(
            name=file_name,
            size_mb=file_size_mb,
            date_upload=timezone.now(),
        )

        # salva fisicamente
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file_name)

        with open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # processa arquivo
        extracted_info = file_obj.process_file(file_path)

        # marca como processado
        file_obj.processed = True
        file_obj.save()

        return ResponseDefault(
            message="Arquivo enviado e processado com sucesso.",
            data={
                "file": {
                    "id": file_obj.id,
                    "name": file_obj.name,
                    "size_mb": file_obj.size_mb,
                    "processed": file_obj.processed,
                    "extracted_info": extracted_info,
                }
            }
        )

import os
from io import BytesIO
from unittest.mock import patch, MagicMock

from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase

from rh.models import File
from access.factories import UserFactory, TokenFactory


class FileViewSetTest(APITestCase):
    
    def setUp(self):
        # Cria usuário + token
        self.user = UserFactory()
        self.token = TokenFactory(user=self.user)

        self.token_header = {
            "HTTP_AUTHORIZATION": f"Bearer {self.token.token}"
        }

        # API KEY opcional (caso use na listagem ou outros endpoints)
        self.api_key_header = {
            "HTTP_X_API_KEY": "j6Q04H4J2pTOCMTLWr9bDpBQerrxU9U"
        }

        # Mocks dos validadores
        self.patch_require_token = patch(
            "common.token.TokenValidator.require_token",
            lambda f: f
        )
        self.patch_require_x_api_key = patch(
            "common.token.TokenValidator.require_x_api_key",
            lambda f: f
        )

        self.patch_require_token.start()
        self.patch_require_x_api_key.start()

    def tearDown(self):
        self.patch_require_token.stop()
        self.patch_require_x_api_key.stop()


    def test_retrieve_success(self):
        f = File.objects.create(
            name="teste.pdf",
            size_mb=1.2,
            date_upload=timezone.now()
        )

        url = reverse("file-detail", args=[f.id])

        res = self.client.get(url, **self.token_header)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["message"], "file retrieved")
        self.assertEqual(res.data["file"]["name"], "teste.pdf")


    def test_retrieve_not_found(self):
        url = reverse("file-detail", args=[99999])

        res = self.client.get(url, **self.token_header)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.data["message"], "file not found")


    def test_upload_no_file(self):
        url = reverse("file-upload")

        res = self.client.post(url, {}, **self.token_header)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data["message"], "Nenhum arquivo enviado.")


    @patch("rh.models.PDFExtractor")
    def test_upload_pdf_success(self, mock_extractor):
        extractor_instance = MagicMock()
        extractor_instance.pdf_with_text.return_value = True
        extractor_instance.extract_resume_info.return_value = {"nome": "Miguel"}
        extractor_instance.extract_entities.return_value = [{"entity": "Python"}]
        mock_extractor.return_value = extractor_instance

        pdf_bytes = BytesIO(b"%PDF-1.4 Fake PDF")
        uploaded_file = SimpleUploadedFile(
            "cv.pdf", pdf_bytes.read(), content_type="application/pdf"
        )

        url = reverse("file-upload")

        res = self.client.post(url, {"file": uploaded_file}, **self.token_header)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["message"], "Arquivo enviado e processado com sucesso.")
        self.assertTrue(res.data["file"]["processed"])
        self.assertEqual(res.data["file"]["extracted_info"]["info"]["nome"], "Miguel")


    @patch("rh.models.PDFExtractor")
    def test_file_saved_to_disk(self, mock_extractor):
        mock_extractor.return_value = MagicMock(pdf_with_text=lambda: False)

        pdf = SimpleUploadedFile("test.pdf", b"%PDF-1.4", content_type="application/pdf")

        url = reverse("file-upload")
        self.client.post(url, {"file": pdf}, **self.token_header)

        path = "uploads/test.pdf"
        self.assertTrue(os.path.exists(path))

        os.remove(path)


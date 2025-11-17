from django.urls import reverse
from rest_framework.test import APITestCase
from unittest.mock import patch

from company.models import Candidate
from company.factories import CandidateFactory

from access.factories import UserFactory, TokenFactory


class CandidateViewSetTest(APITestCase):

    def setUp(self):
        # Usuário + token para retrieve
        self.user = UserFactory()
        self.token = TokenFactory(user=self.user)

        self.token_header = {
            "HTTP_AUTHORIZATION": f"Bearer {self.token.token}"
        }

        self.api_key_header = {
            "HTTP_X_API_KEY": "j6Q04H4J2pTOCMTLWr9bDpBQerrxU9U"
        }

        # mocks do token validator
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

    # ---------------------------
    # LIST
    # ---------------------------
    def test_list_candidates_success(self):
        CandidateFactory.create_batch(3)

        url = reverse("candidate-list")

        res = self.client.get(url, **self.api_key_header)

        self.assertEqual(res.status_code, 200)
        self.assertIn("candidates", res.data)
        self.assertEqual(len(res.data["candidates"]), 3)
        self.assertEqual(res.data["message"], "list of candidates")

    # ---------------------------
    # RETRIEVE
    # ---------------------------
    def test_retrieve_candidate_success(self):
        c = CandidateFactory()

        url = reverse("candidate-detail", kwargs={"pk": c.pk})

        res = self.client.get(url, **self.token_header)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["message"], "candidate retrieved")
        self.assertEqual(res.data["candidate"]["id"], c.pk)

    def test_retrieve_candidate_not_found(self):
        url = reverse("candidate-detail", kwargs={"pk": 9999})

        res = self.client.get(url, **self.token_header)

        self.assertEqual(res.status_code, 404)
        self.assertIn("candidate not found", res.data["message"])

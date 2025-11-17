from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from ai.models import Queries
from ai.serializer import QuerieSerializer
from ai.factories import QueriesFactory

from access.models import User, Token
from access.factories import UserFactory, TokenFactory


class QuerieViewSetTest(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.token = TokenFactory(user=self.user)

        self.token_header = {'HTTP_AUTHORIZATION': f'Bearer {self.token.token}'}

        # Mock token validator
        self.patch_require_token = patch(
            'common.token.TokenValidator.require_token',
            lambda f: f
        )
        self.patch_require_token.start()

        self.data = {
            "prompt": "qual é a capital da França?"
        }

    def tearDown(self):
        self.patch_require_token.stop()

    # LIST
    def test_list_queries(self):
        QueriesFactory.create_batch(3)

        url = reverse('queries-list')
        res = self.client.get(url, **self.token_header)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 3)

    # RETRIEVE
    def test_retrieve_query(self):
        q = QueriesFactory()

        url = reverse('queries-detail', kwargs={'pk': q.pk})
        res = self.client.get(url, **self.token_header)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["id"], q.id)

    # CREATE
    def test_create_query(self):
        url = reverse('queries-prompt')
        payload = {"prompt": "testando criação"}

        res = self.client.post(url, payload, format="json", **self.token_header)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(Queries.objects.count(), 1)

    # UPDATE
    def test_update_query(self):
        q = QueriesFactory()

        url = reverse('queries-detail', kwargs={"pk": q.pk})

        res = self.client.patch(url, {"prompt": "novo valor"}, format="json", **self.token_header)

        self.assertEqual(res.status_code, 200)

        q.refresh_from_db()
        self.assertEqual(q.ask, "novo valor")

    # DELETE
    def test_delete_query(self):
        q = QueriesFactory()

        url = reverse('queries-detail', kwargs={"pk": q.pk})
        res = self.client.delete(url, **self.token_header)

        self.assertEqual(res.status_code, 204)
        self.assertEqual(Queries.objects.count(), 0)

    # ACTION: prompt
    def test_prompt_success(self):
        url = reverse('queries-prompt')

        res = self.client.post(url, self.data, format='json', **self.token_header)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["query"], self.data["prompt"])

    def test_prompt_missing_prompt(self):
        url = reverse('queries-prompt')

        res = self.client.post(url, {}, format='json', **self.token_header)

        self.assertEqual(res.status_code, 400)
        self.assertIn("Nenhum prompt enviado", res.data["message"])

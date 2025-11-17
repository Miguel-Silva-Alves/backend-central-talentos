import factory
from ai.models import Queries
from access.factories import UserFactory

class QueriesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Queries

    ask = factory.Sequence(lambda n: f"Pergunta {n}")
    answer = None
    user = factory.SubFactory(UserFactory)


import factory
from datetime import date, timedelta
from faker import Faker
from .models import Candidate
from access.factories import UserFactory

fake = Faker()


class CandidateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Candidate

    name = factory.Faker("name")
    email = factory.Sequence(lambda n: f"candidate{n}@example.com")
    phone = factory.Faker("msisdn")
    years_experience = factory.Faker("random_int", min=0, max=30)
    location = factory.Faker("city")
    current_position = factory.Faker("job")

    user_creator = factory.SubFactory(UserFactory)

    birth_date = factory.LazyFunction(
        lambda: date.today() - timedelta(days=365 * fake.random_int(min=20, max=50))
    )

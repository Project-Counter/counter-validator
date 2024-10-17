import factory
import faker
from core.fake_data import UserFactory
from counter.fake_data import PlatformFactory

from validations.models import Validation, ValidationCore

fake = faker.Faker(locale="en_US")


class ValidationCoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ValidationCore

    platform = factory.SubFactory(PlatformFactory)
    platform_name = factory.lazy_attribute(
        lambda o: o.platform.name if o.platform else fake.company()
    )


class ValidationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Validation

    core = factory.SubFactory(ValidationCoreFactory)
    user = factory.SubFactory(UserFactory)
    filename = factory.Faker("file_name")
    file = factory.django.FileField(filename="test.txt")
    user_note = factory.Faker("text")

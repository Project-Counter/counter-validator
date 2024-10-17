import factory

from counter.models import Platform


class PlatformFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Platform

    id = factory.Faker("uuid4")
    name = factory.Faker("company")
    abbrev = factory.Faker("lexify", text="????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    website = factory.Faker("url")

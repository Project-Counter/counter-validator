import factory

from counter.models import Platform, SushiService

REPORT_TYPE_CODES = [
    "TR",
    "TR_J1",
    "TR_J2",
    "TR_J3",
    "TR_J4",
    "TR_B1",
    "TR_B2",
    "TR_B3",
    "PR",
    "PR_P1",
    "DR",
    "DR_D1",
    "DR_D2",
    "IR",
    "IR_A1",
    "IR_M1",
]

COP_VERSIONS = ["5.0", "5.1"]


class PlatformFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Platform

    id = factory.Faker("uuid4")
    name = factory.Faker("company")
    abbrev = factory.Faker("lexify", text="????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    website = factory.Faker("url")


class SushiServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SushiService

    id = factory.Faker("uuid4")
    counter_release = factory.Faker("random_element", elements=COP_VERSIONS)
    url = factory.Faker("url")
    platform = factory.SubFactory(PlatformFactory)
    ip_address_authorization = factory.Faker("boolean")
    api_key_required = factory.Faker("boolean")
    platform_attr_required = factory.Faker("boolean")
    requestor_id_required = factory.Faker("boolean")

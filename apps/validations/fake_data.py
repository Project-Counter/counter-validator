import factory.fuzzy
import faker
from core.fake_data import UserFactory
from counter.fake_data import COP_VERSIONS, REPORT_TYPE_CODES, PlatformFactory
from counter.logic.dates import month_end

from validations.models import CounterAPIValidation, Validation, ValidationCore

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


class CounterAPICredentialsFactory(factory.Factory):
    requestor_id = factory.Faker("uuid4")
    customer_id = factory.Faker("company")
    api_key = factory.Faker("uuid4")


class CounterAPIValidationRequestDataFactory(factory.Factory):
    credentials = factory.LazyFunction(
        lambda: factory.build(dict, FACTORY_CLASS=CounterAPICredentialsFactory)
    )
    url = factory.Faker("url")
    report_code = factory.fuzzy.FuzzyChoice(REPORT_TYPE_CODES)
    cop_version = factory.fuzzy.FuzzyChoice(COP_VERSIONS)
    begin_date = factory.LazyFunction(
        lambda: fake.date_this_decade(before_today=True).replace(day=1)
    )
    end_date = factory.LazyAttribute(lambda o: month_end(o.begin_date))
    extra_attributes = factory.LazyFunction(dict)


class CounterAPIValidationFactory(ValidationFactory):
    class Meta:
        model = CounterAPIValidation

    url = factory.Faker("url")
    requested_report_code = factory.fuzzy.FuzzyChoice(REPORT_TYPE_CODES)
    requested_cop_version = factory.fuzzy.FuzzyChoice(COP_VERSIONS)
    requested_begin_date = factory.LazyFunction(
        lambda: fake.date_this_decade(before_today=True).replace(day=1)
    )
    requested_end_date = factory.LazyAttribute(lambda o: month_end(o.requested_begin_date))
    requested_extra_attributes = factory.LazyFunction(dict)

    @factory.post_generation
    def credentials(self, create, extracted, **kwargs):
        if extracted:
            self.credentials = extracted
        else:
            self.credentials = factory.build(
                dict, FACTORY_CLASS=CounterAPICredentialsFactory, **kwargs
            )

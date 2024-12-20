import factory.fuzzy
import faker
from core.fake_data import UserFactory
from counter.fake_data import COP_VERSIONS, REPORT_TYPE_CODES
from counter.logic.dates import month_end

from validations.enums import SeverityLevel
from validations.hashing import checksum_string
from validations.models import CounterAPIValidation, Validation, ValidationCore, ValidationMessage

fake = faker.Faker(locale="en_US")


class ValidationCoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ValidationCore

    user = factory.SubFactory(UserFactory)
    user_email_checksum = factory.LazyAttribute(lambda o: checksum_string(o.user.email))
    validation_result = SeverityLevel.NOTICE


class ValidationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Validation

    core = factory.SubFactory(ValidationCoreFactory)
    filename = factory.Faker("file_name")
    file = factory.django.FileField(filename="test.txt")
    user_note = factory.Faker("text")

    @factory.post_generation
    def messages(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for i, m in enumerate(extracted):
                m.validation = self
                m.number = i + 1
            self.messages.set(extracted)
        elif count := kwargs.pop("count", 0):
            to_add = []
            for index, m in enumerate(ValidationMessageFactory.build_batch(count, validation=self)):
                m.number = index
                to_add.append(m)
            ValidationMessage.objects.bulk_create(to_add)


class CounterAPICredentialsFactory(factory.Factory):
    requestor_id = factory.Faker("uuid4")
    customer_id = factory.Faker("company")
    api_key = factory.Faker("uuid4")
    platform = factory.LazyFunction(lambda: fake.boolean() and fake.company() or None)


class CounterAPIValidationRequestDataFactory(factory.Factory):
    credentials = factory.LazyFunction(
        lambda: factory.build(dict, FACTORY_CLASS=CounterAPICredentialsFactory)
    )
    url = factory.Faker("url")
    api_endpoint = "/reports/[id]"
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


class MessageDictFactory(factory.Factory):
    class Meta:
        model = dict

    d = factory.Faker("text")
    l = factory.fuzzy.FuzzyChoice(SeverityLevel.labels)  # noqa: E741
    h = factory.Faker("sentence")
    p = factory.Faker("sentence")
    m = factory.Faker("sentence")
    s = factory.Faker("sentence")


class ValidationMessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ValidationMessage

    validation = factory.SubFactory(ValidationFactory)
    number = factory.Sequence(lambda n: n)
    data = factory.Faker("text")
    severity = factory.fuzzy.FuzzyChoice(SeverityLevel.values)
    code = factory.Faker("bothify", text="?###")
    location = factory.Faker("sentence")
    message = factory.Faker("sentence")
    summary = factory.Faker("sentence")
    hint = factory.Faker("sentence")

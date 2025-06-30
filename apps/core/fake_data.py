import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    is_active = True
    is_validator_admin = False
    receive_operator_emails = factory.LazyAttribute(lambda o: o.is_validator_admin)

    @factory.post_generation
    def verified_email(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.emailaddress_set.create(email=self.email, verified=True)

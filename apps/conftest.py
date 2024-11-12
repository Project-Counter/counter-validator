import pytest
from core.fake_data import UserFactory
from core.models import UserApiKey
from rest_framework.test import APIClient


@pytest.fixture
def normal_user():
    return UserFactory()


@pytest.fixture
def client_unauthenticated():
    return APIClient()


@pytest.fixture
def client_authenticated_user(normal_user):
    client = APIClient()
    client.force_login(normal_user)
    return client


@pytest.fixture
def client_with_api_key(normal_user):
    api_key, key = UserApiKey.objects.create_key(name="foo", user=normal_user)
    client = APIClient(headers={"Authorization": f"Api-Key {key}"})
    client.user_ = normal_user
    client.api_key_prefix_ = api_key.prefix
    return client

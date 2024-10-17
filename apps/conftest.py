import pytest
from core.fake_data import UserFactory
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

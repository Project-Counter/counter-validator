import pytest
from core.fake_data import UserFactory
from core.models import UserApiKey
from rest_framework.test import APIClient


@pytest.fixture
def normal_user():
    return UserFactory()


@pytest.fixture
def validator_admin_user():
    return UserFactory(is_validator_admin=True)


@pytest.fixture
def client_unauthenticated():
    return APIClient()


@pytest.fixture
def client_authenticated_user(normal_user):
    client = APIClient()
    client.force_login(normal_user)
    return client


@pytest.fixture
def client_validator_admin_user(validator_admin_user):
    client = APIClient()
    client.force_login(validator_admin_user)
    return client


@pytest.fixture
def client_with_api_key(normal_user):
    api_key, key = UserApiKey.objects.create_key(name="foo", user=normal_user)
    client = APIClient(headers={"Authorization": f"Api-Key {key}"})
    client.user_ = normal_user
    client.api_key_prefix_ = api_key.prefix
    return client


@pytest.fixture
def users_and_clients(
    normal_user,
    client_unauthenticated,
    client_with_api_key,
    client_validator_admin_user,
    client_authenticated_user,
    validator_admin_user,
    admin_client,
    admin_user,
):
    return {
        "unauthenticated": (None, client_unauthenticated),
        "normal": (normal_user, client_authenticated_user),
        "su": (admin_user, admin_client),
        "admin": (validator_admin_user, client_validator_admin_user),
        "api_key_normal": (normal_user, client_with_api_key),
    }


def _client_and_status_code(request, users_and_clients) -> tuple[APIClient, int]:
    """
    Returns a tuple of client and status code for views which should only allow admins and no
    API key access
    """
    user_type, status_code = request.param
    return users_and_clients[user_type][1], status_code


status_code_by_user_admin_only = [
    pytest.param(("unauthenticated", 403), id="unauthenticated"),
    pytest.param(("normal", 403), id="normal"),
    pytest.param(("su", 200), id="su"),
    pytest.param(("admin", 200), id="admin"),
    pytest.param(("api_key_normal", 403), id="api_key_normal"),
]


client_and_status_code_admin_only = pytest.fixture(
    _client_and_status_code, params=status_code_by_user_admin_only
)


status_code_by_user_any_authenticated = [
    pytest.param(("unauthenticated", 403), id="unauthenticated"),
    pytest.param(("normal", 200), id="normal"),
    pytest.param(("su", 200), id="su"),
    pytest.param(("admin", 200), id="admin"),
    pytest.param(("api_key_normal", 403), id="api_key_normal"),
]


client_and_status_code_any_authenticated = pytest.fixture(
    _client_and_status_code, params=status_code_by_user_any_authenticated
)

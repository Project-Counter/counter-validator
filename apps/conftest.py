import pytest
from core.fake_data import UserFactory
from core.models import UserApiKey
from rest_framework.test import APIClient


@pytest.fixture
def su_user():
    return UserFactory(is_superuser=True, verified_email=True)


@pytest.fixture
def normal_user():
    return UserFactory(verified_email=True)


@pytest.fixture
def validator_admin_user():
    return UserFactory(is_validator_admin=True, verified_email=True)


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
def client_su_user(su_user):
    client = APIClient()
    client.force_login(su_user)
    return client


@pytest.fixture
def client_with_api_key(normal_user):
    api_key, key = UserApiKey.objects.create_key(name="foo", user=normal_user)
    client = APIClient(headers={"Authorization": f"Api-Key {key}"})
    client.user_ = normal_user
    client.api_key_prefix_ = api_key.prefix
    return client


@pytest.fixture
def client_with_api_key_admin(validator_admin_user):
    api_key, key = UserApiKey.objects.create_key(name="foo", user=validator_admin_user)
    client = APIClient(headers={"Authorization": f"Api-Key {key}"})
    client.user_ = validator_admin_user
    client.api_key_prefix_ = api_key.prefix
    return client


@pytest.fixture
def users_and_clients(
    normal_user,
    client_unauthenticated,
    client_with_api_key,
    client_with_api_key_admin,
    client_validator_admin_user,
    client_authenticated_user,
    validator_admin_user,
    su_user,
    client_su_user,
):
    return {
        "unauthenticated": (None, client_unauthenticated),
        "normal": (normal_user, client_authenticated_user),
        "su": (su_user, client_su_user),
        "admin": (validator_admin_user, client_validator_admin_user),
        "api_key_normal": (normal_user, client_with_api_key),
        "api_key_admin": (validator_admin_user, client_with_api_key_admin),
    }


def _client_and_status_code(request, users_and_clients) -> tuple[APIClient, int]:
    """
    Helper function which generates combinations of client and expected status code
    based on the passed params.
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


@pytest.fixture(
    params=["unauthenticated", "normal", "su", "admin", "api_key_normal", "api_key_admin"]
)
def all_clients(request, users_and_clients):
    return users_and_clients[request.param][1]

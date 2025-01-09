import pytest

from core.models import User


@pytest.mark.django_db
class TestUserManager:
    def test_create_user(self):
        user = User.objects.create_user(email="foo@bar.baz", password="password")
        assert user.email == "foo@bar.baz"
        assert user.is_superuser is False

    def test_create_superuser(self):
        user = User.objects.create_superuser(email="foo@bar.baz", password="password")
        assert user.email == "foo@bar.baz"
        assert user.is_superuser is True

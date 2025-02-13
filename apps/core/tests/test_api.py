import re

import pytest
from allauth.account.models import EmailAddress
from django.urls import reverse

from ..fake_data import UserFactory
from ..models import User, UserApiKey


@pytest.mark.django_db
class TestUserDetailAPI:
    def test_user_detail_access(self, client_and_status_code_any_authenticated):
        client, status_code = client_and_status_code_any_authenticated
        res = client.get(reverse("current-user"))
        assert res.status_code == status_code

    def test_user_detail(self, client_authenticated_user, normal_user):
        res = client_authenticated_user.get(reverse("current-user"))
        assert res.status_code == 200, "user should see his details"
        assert res.data["id"] == normal_user.id
        assert res.json()["email"] == normal_user.email
        assert res.json()["first_name"] == normal_user.first_name
        assert res.json()["last_name"] == normal_user.last_name
        assert res.json()["is_validator_admin"] == normal_user.is_validator_admin
        assert res.json()["is_superuser"] == normal_user.is_superuser
        assert res.json()["has_admin_role"] == normal_user.has_admin_role
        assert res.json()["verified_email"] == normal_user.verified_email


@pytest.mark.django_db
class TestUserManagementAPI:
    def test_user_list_access(self, client_and_status_code_admin_only):
        client, status_code = client_and_status_code_admin_only
        res = client.get(reverse("user-list"))
        assert res.status_code == status_code

    @pytest.mark.parametrize(
        ["user_type", "can_see_superusers"],
        [
            ("unauthenticated", None),
            ("normal", None),
            ("su", True),
            ("admin", False),
            ("api_key_normal", None),
        ],
    )
    def test_user_list_visibility(self, users_and_clients, user_type, can_see_superusers):
        """
        Test that only superusers can see other superusers.
        """
        user, client = users_and_clients[user_type]
        res = client.get(reverse("user-list"))
        if can_see_superusers is None:
            assert res.status_code == 403
        else:
            assert res.status_code == 200
            assert len(res.json()) == (3 if can_see_superusers else 2)

    def test_user_list_content(self, users_and_clients):
        res = users_and_clients["su"][1].get(reverse("user-list"))
        assert res.status_code == 200
        assert len(res.json()) == 3
        first = res.json()[0]
        assert set(first.keys()) == {
            "id",
            "email",
            "first_name",
            "last_name",
            "has_admin_role",
            "is_validator_admin",
            "is_superuser",
            "is_active",
            "last_login",
            "verified_email",
        }

    def test_user_list_efficiency(self, client_validator_admin_user, django_assert_max_num_queries):
        """
        Test that there are no n+1 queries.
        """
        UserFactory.create_batch(50)
        with django_assert_max_num_queries(9):
            res = client_validator_admin_user.get(reverse("user-list"))
            assert res.status_code == 200
            assert len(res.json()) == 51, "50 users + current user"

    def test_user_detail(self, client_validator_admin_user, normal_user):
        res = client_validator_admin_user.get(reverse("user-detail", kwargs={"pk": normal_user.pk}))
        assert res.status_code == 200
        assert res.json()["id"] == normal_user.id
        assert res.json()["email"] == normal_user.email
        assert res.json()["first_name"] == normal_user.first_name
        assert res.json()["last_name"] == normal_user.last_name
        assert res.json()["is_validator_admin"] == normal_user.is_validator_admin
        assert res.json()["is_superuser"] == normal_user.is_superuser

    @pytest.mark.parametrize("verified", [True, False, None])
    def test_user_verified_email(self, client_validator_admin_user, verified):
        user = UserFactory()
        if verified is not None:
            EmailAddress.objects.create(user=user, email=user.email, verified=verified)
        res = client_validator_admin_user.get(reverse("user-detail", kwargs={"pk": user.pk}))
        assert res.status_code == 200
        assert res.json()["verified_email"] == bool(verified)

    @pytest.mark.parametrize(
        ["email", "status_code"],
        [
            ("foo@bar.baz", 201),
            ("", 400),
            ("foo@bar", 400),
        ],
    )
    def test_user_create(self, client_validator_admin_user, email, status_code):
        res = client_validator_admin_user.post(reverse("user-list"), data={"email": email})
        assert res.status_code == status_code

    def test_user_create_data(self, client_validator_admin_user):
        res = client_validator_admin_user.post(
            reverse("user-list"),
            data={
                "email": "foo@bar.baz",
                "first_name": "foo",
                "last_name": "bar",
                "is_validator_admin": True,
                "is_superuser": True,
            },
        )
        assert res.status_code == 201
        assert res.json()["email"] == "foo@bar.baz"
        assert res.json()["first_name"] == "foo"
        assert res.json()["last_name"] == "bar"
        assert res.json()["is_validator_admin"] is True
        assert res.json()["is_superuser"] is True
        user = User.objects.get(pk=res.json()["id"])
        assert user.email == "foo@bar.baz"

    def test_user_update(self, client_validator_admin_user, normal_user):
        res = client_validator_admin_user.patch(
            reverse("user-detail", kwargs={"pk": normal_user.pk}),
            data={"first_name": "foo"},
        )
        assert res.status_code == 200
        assert res.json()["first_name"] == "foo"
        normal_user.refresh_from_db()
        assert normal_user.first_name == "foo"

    def test_user_delete(self, client_validator_admin_user, normal_user):
        res = client_validator_admin_user.delete(
            reverse("user-detail", kwargs={"pk": normal_user.pk})
        )
        assert res.status_code == 204
        assert not User.objects.filter(pk=normal_user.pk).exists()

    @pytest.mark.parametrize(
        ["user_type", "can_delete"],
        [
            ("unauthenticated", None),
            ("normal", None),
            ("su", True),
            ("admin", False),
            ("api_key_normal", None),
        ],
    )
    def test_only_superuser_can_delete_superuser(self, users_and_clients, user_type, can_delete):
        user, client = users_and_clients[user_type]
        su_user = UserFactory(is_superuser=True)
        res = client.delete(reverse("user-detail", kwargs={"pk": su_user.pk}))
        if can_delete is None:
            assert res.status_code == 403
        elif can_delete:
            assert res.status_code == 204
            assert not User.objects.filter(pk=su_user.pk).exists()
        else:
            assert res.status_code == 404
            assert User.objects.filter(pk=su_user.pk).exists()

    @pytest.mark.parametrize(
        ["user_type"], [["normal"], ["su"], ["admin"], ["api_key_normal"], ["api_key_admin"]]
    )
    def test_user_cannot_delete_self(self, users_and_clients, user_type):
        user, client = users_and_clients[user_type]
        res = client.delete(reverse("user-detail", kwargs={"pk": user.pk}))
        assert res.status_code == 403
        assert User.objects.filter(pk=user.pk).exists()

    @pytest.mark.parametrize(
        ["user_type", "status_code"],
        [
            ["normal", 403],
            ["su", 200],  # can edit self, but change of validation admin is not made
            ["admin", 200],  # can edit self, but change of validation admin is not made
            ["api_key_normal", 403],
            ["api_key_admin", 403],
        ],
    )
    def test_user_cannot_change_is_validator_admin_on_self(
        self, users_and_clients, user_type, status_code
    ):
        user, client = users_and_clients[user_type]
        old_value = user.is_validator_admin
        res = client.patch(
            reverse("user-detail", kwargs={"pk": user.pk}),
            data={"is_validator_admin": not user.is_validator_admin},
        )
        assert res.status_code == status_code
        user.refresh_from_db()
        assert user.is_validator_admin == old_value

    @pytest.mark.parametrize(
        ["user_type", "status_code"],
        [
            ["normal", 403],
            ["su", 200],  # can edit self, but change of is_active is not made
            ["admin", 200],  # can edit self, but change of is_active admin is not made
            ["api_key_normal", 403],
            ["api_key_admin", 403],
        ],
    )
    def test_user_cannot_deactivate_self(self, users_and_clients, user_type, status_code):
        user, client = users_and_clients[user_type]
        res = client.patch(
            reverse("user-detail", kwargs={"pk": user.pk}),
            data={"is_active": False},
        )
        assert res.status_code == status_code
        user.refresh_from_db()
        assert user.is_active


@pytest.mark.django_db
class TestApiKeyAPI:
    def test_api_key_list(
        self, client_authenticated_user, django_assert_max_num_queries, normal_user
    ):
        for i in range(10):
            UserApiKey.objects.create_key(name=f"key-{i}", user=normal_user)
        with django_assert_max_num_queries(9):
            res = client_authenticated_user.get(reverse("api-key-list"))
            assert res.status_code == 200
            assert len(res.json()) == 10

    def test_api_key_detail(self, client_authenticated_user, normal_user):
        api_key, key = UserApiKey.objects.create_key(name="foo", user=normal_user)
        res = client_authenticated_user.get(
            reverse("api-key-detail", kwargs={"prefix": api_key.prefix})
        )
        assert res.status_code == 200
        assert res.json()["name"] == "foo"

    def test_api_key_create(self, client_authenticated_user):
        res = client_authenticated_user.post(reverse("api-key-list"), data={"name": "foo"})
        assert res.status_code == 201
        assert "key" in res.json()

    def test_api_key_revoke(self, client_authenticated_user, normal_user):
        api_key, key = UserApiKey.objects.create_key(name="foo", user=normal_user)
        res = client_authenticated_user.delete(
            reverse("api-key-detail", kwargs={"prefix": api_key.prefix})
        )
        assert res.status_code == 200
        assert UserApiKey.objects.get(prefix=api_key.prefix).revoked


@pytest.mark.django_db
class TestRegistrationAPI:
    def test_registration(self, client_unauthenticated):
        res = client_unauthenticated.post(
            reverse("rest_register"),
            data={
                "email": "foo@bar.baz",
                "password1": "fksldj2938wflkjsw",
                "password2": "fksldj2938wflkjsw",
            },
        )
        assert res.status_code == 204
        assert User.objects.filter(email="foo@bar.baz").exists()

    def test_registration_invalid_email(self, client_unauthenticated):
        res = client_unauthenticated.post(
            reverse("rest_register"),
            data={
                "email": "foo@bar",
                "password1": "fksldj2938wflkjsw",
                "password2": "fksldj2938wflkjsw",
            },
        )
        assert res.status_code == 400

    def test_registration_already_used_email(self, client_unauthenticated, normal_user):
        res = client_unauthenticated.post(
            reverse("rest_register"),
            data={
                "email": normal_user.email,
                "password1": "fksldj2938wflkjsw",
                "password2": "fksldj2938wflkjsw",
            },
        )
        assert res.status_code == 400
        assert res.json() == {"email": ["A user is already registered with this e-mail address."]}

    def test_names_are_stored(self, client_unauthenticated):
        res = client_unauthenticated.post(
            reverse("rest_register"),
            data={
                "email": "foo@bar.baz",
                "first_name": "Foo",
                "last_name": "Bar",
                "password1": "fksld39082dwfjl",
                "password2": "fksld39082dwfjl",
            },
        )
        assert res.status_code == 204
        user = User.objects.get(email="foo@bar.baz")
        assert user.first_name == "Foo"
        assert user.last_name == "Bar"


@pytest.mark.django_db
class TestPasswordReset:
    def test_password_reset_email_sending(self, client_unauthenticated, normal_user, mailoutbox):
        assert len(mailoutbox) == 0
        res = client_unauthenticated.post(
            reverse("rest_password_reset"),
            data={"email": normal_user.email},
        )
        assert res.status_code == 200
        assert len(mailoutbox) == 1

    def test_password_reset_from_email_link(self, client_unauthenticated, normal_user, mailoutbox):
        """
        Test that the password reset link works.
        """
        assert len(mailoutbox) == 0
        res = client_unauthenticated.post(
            reverse("rest_password_reset"),
            data={"email": normal_user.email},
        )
        assert res.status_code == 200
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        m = re.search(r"\?uid=(\S+)&token=(\S+)", mail.body)
        assert m
        uid, token = m.groups()
        res = client_unauthenticated.post(
            reverse("rest_password_reset_confirm"),
            data={
                "uid": uid,
                "token": token,
                "new_password1": "new_password1",
                "new_password2": "new_password1",
            },
        )
        assert res.status_code == 200

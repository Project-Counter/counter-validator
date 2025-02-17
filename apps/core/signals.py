from allauth.account.models import EmailAddress
from allauth.account.signals import user_signed_up
from django.dispatch import Signal, receiver

from .tasks import async_mail_admins

password_reset_signal = Signal()


@receiver(user_signed_up)
def mail_about_user_signing_up(request, user, **kwargs):
    async_mail_admins.delay(
        f"New user registered - {user.email}",
        f"""\
A new user has registered.

Email: {user.email}
First name: {user.first_name}
Last name: {user.last_name}
""",
    )


@receiver(password_reset_signal)
def verify_user_email(request, user, **kwargs):
    """
    After successful password reset, we take the users default email as verified.
    Also, if the appropriate `EmailAddress` instance does not exist, we create it.
    """
    if user.email and not user.verified_email:
        email_obj, created = EmailAddress.objects.get_or_create(
            user=user, email=user.email, defaults={"verified": True}
        )
        if not created:
            email_obj.verified = True
            email_obj.save()

import celery
from django.conf import settings
from django.core.mail import mail_admins, send_mail


@celery.shared_task
def async_mail_admins(subject, body):
    mail_admins(subject, body)


@celery.shared_task
def async_mail_operators(subject, body):
    """
    Send email to operators (defaults to ADMINS if OPERATORS not specified).
    Uses the OPERATORS setting from Django settings.
    """
    if not settings.OPERATORS:
        # If no operators are configured, don't send any emails
        return

    # Extract email addresses from the OPERATORS setting
    # OPERATORS is a tuple of tuples, where each inner tuple is (name, email)
    operator_recipients = [f"{name} <{email}>" for name, email in settings.OPERATORS]

    if operator_recipients:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=operator_recipients,
            fail_silently=False,
        )

from datetime import timedelta

import celery
from django.conf import settings
from django.core.mail import mail_admins, send_mail
from django.utils.timezone import now
from validations.models import ValidationCore


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


@celery.shared_task
def daily_validation_report():
    """
    Send daily validation report to operators with statistics from the last 24 hours.
    """
    # Calculate the time range for the last 24 hours
    end_time = now()
    start_time = end_time - timedelta(hours=24)

    # Get validation count for the last 24 hours
    validation_count = ValidationCore.objects.filter(created__gte=start_time).count()

    # Format the date range for the email
    date_range = (
        f"{start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    subject = f"Daily Validation Report - {end_time.strftime('%Y-%m-%d')}"

    body = f"""Daily Validation Report

Time Period: {date_range}
Total Validations: {validation_count}

This report shows the number of validations performed in the last 24 hours.

---
COUNTER Validator System
"""

    # Send the report to operators
    async_mail_operators.delay(subject, body)

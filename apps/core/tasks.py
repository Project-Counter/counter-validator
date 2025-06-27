from datetime import timedelta

import celery
from django.conf import settings
from django.core.mail import mail_admins, send_mail
from django.db import models
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

    # Get validations grouped by user for the last 24 hours
    user_validations = (
        ValidationCore.objects.filter(created__gte=start_time)
        .values("user__email", "user__first_name", "user__last_name")
        .annotate(count=models.Count("id"))
        .order_by("-count", "user__email")
    )

    # Get validations grouped by CoP version for the last 24 hours
    cop_version_validations = (
        ValidationCore.objects.filter(created__gte=start_time)
        .values("cop_version")
        .annotate(count=models.Count("id"))
        .order_by("-count", "cop_version")
    )

    # Format the date range for the email
    date_range = (
        f"{start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    subject = f"Daily Validation Report - {end_time.strftime('%Y-%m-%d')}"

    # Build the user statistics table
    user_table = ""
    if user_validations:
        user_table += "-" * 60 + "\n"
        user_table += f"{'User':<40} {'Validations':<10}\n"
        user_table += "-" * 60 + "\n"

        for user_data in user_validations:
            user_email = user_data["user__email"] or "Unknown"
            if user_name := (
                f"{user_data['user__first_name'] or ''} {user_data['user__last_name'] or ''}"
            ).strip():
                user_display = f"{user_name} ({user_email})"
            else:
                user_display = user_email

            # Truncate user display if too long
            if len(user_display) > 39:
                user_display = user_display[:36] + "..."

            user_table += f"{user_display:<40} {user_data['count']:<10}\n"
    else:
        user_table = "\nNo user activity in the reported period.\n"

    # Build the CoP version statistics table
    cop_version_table = ""
    if cop_version_validations:
        cop_version_table += "-" * 50 + "\n"
        cop_version_table += f"{'CoP Version':<20} {'Validations':<10}\n"
        cop_version_table += "-" * 50 + "\n"

        for cop_data in cop_version_validations:
            cop_version = cop_data["cop_version"] or "Unknown"
            cop_version_table += f"{cop_version:<20} {cop_data['count']:<10}\n"
    else:
        cop_version_table = "\nNo CoP version data in the reported period.\n"

    body = f"""Daily Validation Report

Time Period: {date_range}
Total Validations: {validation_count}

Validations by CoP version:
{cop_version_table}

Validations by user:
{user_table}

---
COUNTER Validator
"""

    # Send the report to operators
    async_mail_operators.delay(subject, body)

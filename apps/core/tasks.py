from datetime import timedelta

import celery
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, mail_admins, send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils.timezone import now
from validations.enums import SeverityLevel
from validations.models import ValidationCore


@celery.shared_task
def async_mail_admins(subject, body):
    mail_admins(subject, body)


@celery.shared_task
def async_mail_operators(subject, text_body, html_body=None):
    """
    Send email to operators and validator admins.

    Args:
        subject: Email subject
        text_body: Plain text email body
        html_body: Optional HTML email body. If provided, sends multipart email
    """
    recipients = set()  # Use set to avoid duplicates

    # Add operators from settings
    if settings.OPERATORS:
        for name, email in settings.OPERATORS:
            recipients.add(f"{name} <{email}>")

    # Add validator admins
    from core.models import User

    validator_admins = User.objects.filter(
        is_validator_admin=True, receive_operator_emails=True, is_active=True
    ).values_list("first_name", "last_name", "email")

    for first_name, last_name, email in validator_admins:
        name = f"{first_name or ''} {last_name or ''}".strip()
        if name:
            recipients.add(f"{name} <{email}>")
        else:
            recipients.add(email)

    if not recipients:
        # If no recipients configured, don't send any emails
        return

    if html_body:
        # Send multipart email with both text and HTML
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=list(recipients),
        )
        email.attach_alternative(html_body, "text/html")
        email.send(fail_silently=False)
    else:
        # Send simple text email
        send_mail(
            subject=subject,
            message=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(recipients),
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
    user_validations_raw = (
        ValidationCore.objects.filter(created__gte=start_time)
        .values("user__email", "user__first_name", "user__last_name")
        .annotate(count=models.Count("id"))
        .order_by("-count", "user__email")
    )

    # Get validations grouped by CoP version for the last 24 hours
    cop_version_validations_raw = (
        ValidationCore.objects.filter(created__gte=start_time)
        .values("cop_version")
        .annotate(count=models.Count("id"))
        .order_by("-count", "cop_version")
    )

    # Get validations grouped by validation result for the last 24 hours
    validation_result_validations_raw = (
        ValidationCore.objects.filter(created__gte=start_time)
        .values("validation_result")
        .annotate(count=models.Count("id"))
        .order_by("-count", "validation_result")
    )

    # Format the date range for the email
    date_range = (
        f"{start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # Prepare user data for templates
    user_validations = []
    for user_data in user_validations_raw:
        user_email = user_data["user__email"] or "Unknown"
        user_name = (
            f"{user_data['user__first_name'] or ''} {user_data['user__last_name'] or ''}".strip()
        )
        user_validations.append(
            {
                "user_email": user_email,
                "user_name": user_name if user_name else None,
                "count": user_data["count"],
            }
        )

    # Prepare CoP version data for templates
    cop_version_validations = []
    for cop_data in cop_version_validations_raw:
        cop_version_validations.append(
            {"cop_version": cop_data["cop_version"] or "Unknown", "count": cop_data["count"]}
        )

    # Prepare validation result data for templates
    validation_result_validations = []
    for result_data in validation_result_validations_raw:
        # Get the display name for the validation result
        try:
            result_display = SeverityLevel(result_data["validation_result"]).label
        except ValueError:
            result_display = "Unknown"

        validation_result_validations.append(
            {"validation_result": result_display, "count": result_data["count"]}
        )

    # Build plain text tables for the text template
    user_table = ""
    if user_validations:
        user_table = "\n" + "-" * 60 + "\n"
        user_table += f"{'User':<40} {'Validations':<10}\n"
        user_table += "-" * 60 + "\n"

        for user_data in user_validations:
            if user_data["user_name"]:
                user_display = f"{user_data['user_name']} ({user_data['user_email']})"
            else:
                user_display = user_data["user_email"]

            # Truncate user display if too long
            if len(user_display) > 39:
                user_display = user_display[:36] + "..."

            user_table += f"{user_display:<40} {user_data['count']:<10}\n"
    else:
        user_table = "\nNo user activity in the reported period.\n"

    cop_version_table = ""
    if cop_version_validations:
        cop_version_table = "\n" + "-" * 50 + "\n"
        cop_version_table += f"{'CoP Version':<20} {'Validations':<10}\n"
        cop_version_table += "-" * 50 + "\n"

        for cop_data in cop_version_validations:
            cop_version_table += f"{cop_data['cop_version']:<20} {cop_data['count']:<10}\n"
    else:
        cop_version_table = "\nNo CoP version data in the reported period.\n"

    validation_result_table = ""
    if validation_result_validations:
        validation_result_table = "\n" + "-" * 50 + "\n"
        validation_result_table += f"{'Validation Result':<20} {'Validations':<10}\n"
        validation_result_table += "-" * 50 + "\n"

        for result_data in validation_result_validations:
            validation_result_table += (
                f"{result_data['validation_result']:<20} {result_data['count']:<10}\n"
            )
    else:
        validation_result_table = "\nNo validation result data in the reported period.\n"

    subject = f"Daily Validation Report - {end_time.strftime('%Y-%m-%d')}"

    # Prepare context for templates
    context = {
        "date_range": date_range,
        "validation_count": validation_count,
        "user_validations": user_validations,
        "cop_version_validations": cop_version_validations,
        "validation_result_validations": validation_result_validations,
        "user_table": user_table,
        "cop_version_table": cop_version_table,
        "validation_result_table": validation_result_table,
    }

    # Render both HTML and text versions
    html_body = render_to_string("core/daily_validation_report.html", context)
    text_body = render_to_string("core/daily_validation_report.txt", context)

    # Send the report to operators with both HTML and text versions
    async_mail_operators.delay(subject, text_body, html_body)

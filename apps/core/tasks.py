import celery
from django.core.mail import mail_admins


@celery.shared_task
def async_mail_admins(subject, body):
    mail_admins(subject, body)

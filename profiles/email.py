from django.core.mail import send_mail

from formulavis import settings


class EmailService:

    def __init__(self):
        pass

    @staticmethod
    def send_email(to_email, subject, message):
        if not isinstance(to_email, list):
            to_email = [to_email]
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            to_email,
            fail_silently=False,
        )



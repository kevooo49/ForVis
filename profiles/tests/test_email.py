from unittest import TestCase

from profiles.email import EmailService


class TestEmailService(TestCase):

    def setUp(self):
        super().setUp()
        self.email_service = EmailService()

    def test_send_email(self):
        self.email_service.send_email('test@email.com', 'Subject', 'Message')

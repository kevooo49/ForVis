from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
	help = ''

	def handle(self, *args, **kwargs):
		users = User.objects.all()
		now = datetime.now(tz=timezone.utc)

		for user in users:
			if now - user.last_login > timedelta(days=6*30):
				user.delete()

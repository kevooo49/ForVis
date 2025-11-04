import logging
import os

from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.models import User
from django.dispatch.dispatcher import receiver

from formulavis.settings import MEDIA_URL

logger = logging.getLogger('email_on_exception_logger')

STATUS = (
    ('empty', 'empty'),
    ('pending', 'pending'),
    ('done', 'done'),
)

FORMATS = (
    ('sat_vis_factor', 'sat_vis_factor'),
    ('sat_vis_interaction', 'sat_vis_interaction'),
    ('sat_vis_matrix', 'sat_vis_matrix'),
    ('sat_vis_tree', 'sat_vis_tree'),
    ('sat_vis_cluster', 'sat_vis_cluster'),
    ('sat_vis_resolution', 'sat_vis_resolution'),
    ('sat_vis_directed', 'sat_vis_directed'),
    ('sat_vis_2clause', 'sat_vis_2clause'),
    ('sat_vis_dpll', 'sat_vis_dpll'),
    ('raw', 'raw'),
    ('variables', 'variables'),
    ('maxsat_vis_factor', 'maxsat_vis_factor'),
    ('maxsat_vis_interaction', 'maxsat_vis_interaction'),
    ('maxsat_vis_matrix', 'maxsat_vis_matrix'),
    ('maxsat_vis_tree', 'maxsat_vis_tree'),
    ('maxsat_vis_cluster', 'maxsat_vis_cluster'),
    ('maxsat_vis_resolution', 'maxsat_vis_resolution'),
)


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')

    def __str__(self):
        return str(self.user)


class TextFile(models.Model):
    profile = models.ForeignKey(Profile, related_name='text_files')
    name = models.CharField(max_length=255)
    content = models.FileField(upload_to=MEDIA_URL)
    minimized = models.BooleanField(default=False)
    kind = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class JsonFile(models.Model):
    text_file = models.ForeignKey(TextFile, related_name='json', on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS, default='empty', max_length=10)
    json_format = models.CharField(choices=FORMATS, max_length=255)
    selected_vars = ArrayField(base_field=models.IntegerField(), default=list)
    content = JSONField(default={})
    progress = models.TextField(default="0")
    task_id = models.CharField(default="", max_length=255)

    def __str__(self):
        return f'{self.text_file.name}: {self.json_format}'


@receiver(models.signals.pre_delete, sender=TextFile)
def auto_delete_file_form_disk(sender, instance, **kwargs):
    """
    Delete file from disk after deleting instance
    """
    if not instance.pk:
        return False

    try:
        old_file = TextFile.objects.get(pk=instance.pk).content
    except TextFile.DoesNotExist:
        return False

    if os.path.isfile(old_file.path):
        os.remove(old_file.path)


@receiver(models.signals.post_save, sender=TextFile)
def create_minimized_version(sender, instance, created, *args, **kwargs):
    """
    Run task for creating minimized version for a new file
    """
    if created and not instance.minimized:
        from profiles.tasks import create_minimized
        create_minimized.delay(instance.pk, instance.profile.pk)

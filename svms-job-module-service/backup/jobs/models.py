from django.contrib.auth.models import User
from django.db import models
from django_mysql.models import DjangoMySQLModel
import uuid

class ModuleConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_id = models.CharField(max_length=36, default=None)
    name_singular = models.CharField(max_length=100, default=None)
    name_plural = models.CharField(max_length=100, default=None)
    code = models.CharField(max_length=100, default=None)
    description = models.TextField(blank=True, null=True)
    is_enabled = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=36)
    modified_by = models.CharField(max_length=36)

    def __str__(self):
        return self.slug


class ModuleConfigVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module_config = models.ForeignKey(ModuleConfig, 
                                        related_name='module_config_versions', 
                                        on_delete=models.CASCADE)
    config = models.TextField()
    version = models.IntegerField(default=1)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=36)
    modified_by = models.CharField(max_length=36)

    def __str__(self):
        return f"{self.module_config.slug} {self.version}"


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(ModuleConfigVersion, on_delete=models.CASCADE)
    program_id = models.CharField(max_length=36)
    language = models.CharField(max_length=10, default='en-US')
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    level = models.CharField(max_length=255)
    bill_rate = models.FloatField()
    bill_rate_currency = models.CharField(max_length=3)
    bill_rate_frequency = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    is_enabled = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=36)
    modified_by = models.CharField(max_length=36)

    def __str__(self):
        return f'{self.program_id}: {self.title}'
# Generated by Django 3.0.8 on 2021-01-18 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_distribution', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendorjobmapping',
            name='reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]

# Generated by Django 3.0.8 on 2021-01-27 11:17

from django.db import migrations, models
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('rate_card', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RateCardConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('program_id', models.UUIDField(db_index=True, unique=True)),
                ('config_json', django_mysql.models.JSONField(default=dict)),
            ],
            options={
                'verbose_name': 'Rate Card Config',
                'verbose_name_plural': 'Rate Cards Config',
            },
        ),
    ]

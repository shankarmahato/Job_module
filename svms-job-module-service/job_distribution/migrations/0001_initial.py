# Generated by Django 3.0.8 on 2021-01-01 16:50

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('job', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorJobMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('program_id', models.CharField(db_index=True, max_length=100)),
                ('distribute_type', models.CharField(choices=[('manual', 'Manual'), ('automatic', 'Automatic'), ('scheduled', 'Scheduled')], default='manual', max_length=100)),
                ('vendor_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('vendor_group_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('distribution_id', models.CharField(blank=True, max_length=100, null=True)),
                ('distribute_method', models.CharField(blank=True, choices=[('on_submit', 'On Submit'), ('final_approval', 'Final Approval')], max_length=100, null=True)),
                ('vendor_selection', models.CharField(blank=True, choices=[('industry_region', 'Industry/Region'), ('manual_input', 'Manual Input')], max_length=100, null=True)),
                ('opt_option', models.CharField(choices=[('no_response', 'No Response'), ('opt_in', 'Opt In'), ('opt_out', 'Opt Out')], default='no_response', max_length=100)),
                ('submission_limit', models.IntegerField(blank=True, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.CharField(blank=True, max_length=36, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=36, null=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='vendor_job_mapping', to='job.Job')),
            ],
            options={
                'verbose_name': 'VendorJobMapping',
                'verbose_name_plural': 'VendorJobMappings',
            },
        ),
        migrations.CreateModel(
            name='ScheduleJobVendorMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('program_id', models.CharField(db_index=True, max_length=100)),
                ('distribute_type', models.CharField(choices=[('manual', 'Manual'), ('automatic', 'Automatic'), ('scheduled', 'Scheduled')], default='scheduled', max_length=100)),
                ('vendor_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('vendor_group_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('distribution_id', models.CharField(blank=True, max_length=100, null=True)),
                ('scheduled_datetime', models.DateTimeField(null=True, verbose_name='Scheduled datetime')),
                ('scheduled_status', models.CharField(choices=[('scheduling', 'scheduling'), ('distributed', 'distributed')], default='scheduling', max_length=100)),
                ('submission_limit', models.IntegerField(blank=True, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.CharField(blank=True, max_length=36, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=36, null=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='schedule_job_vendor_mapping', to='job.Job')),
            ],
        ),
    ]
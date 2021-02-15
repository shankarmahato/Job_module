# Generated by Django 3.0.8 on 2021-01-01 16:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_mysql.models
import simple_history.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('job_catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoundationData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('program_id', models.CharField(max_length=50)),
                ('cost_center', models.CharField(blank=True, max_length=255, null=True)),
                ('company_code', models.CharField(blank=True, max_length=255, null=True)),
                ('gl_code', models.CharField(blank=True, max_length=255, null=True)),
                ('source_code', models.CharField(blank=True, max_length=255, null=True)),
                ('market_region', models.CharField(blank=True, max_length=255, null=True)),
                ('work_location', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.BooleanField(db_index=True, default=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.CharField(blank=True, max_length=50, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'Foundation Data',
                'verbose_name_plural': 'Foundation Data',
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('job_manager', models.CharField(blank=True, max_length=50, null=True)),
                ('msp_manager', models.CharField(blank=True, max_length=50, null=True)),
                ('program_id', models.CharField(blank=True, db_index=True, max_length=50, null=True)),
                ('type', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('hire_type', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('company_name', models.CharField(blank=True, db_index=True, max_length=200, null=True)),
                ('level', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('no_of_openings', models.IntegerField(blank=True, null=True)),
                ('location_id', models.CharField(blank=True, db_index=True, default=0, max_length=100, null=True)),
                ('salary_min_range', models.IntegerField(blank=True, null=True)),
                ('salary_max_range', models.IntegerField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('start_date', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('hierarchy', models.CharField(blank=True, max_length=256, null=True)),
                ('hierarchy_location', models.CharField(blank=True, max_length=256, null=True)),
                ('currency', models.CharField(blank=True, max_length=200, null=True)),
                ('min_bill_rate', models.FloatField(blank=True, null=True)),
                ('max_bill_rate', models.FloatField(blank=True, null=True)),
                ('shift', models.CharField(blank=True, max_length=100, null=True)),
                ('qualifications', django_mysql.models.JSONField(blank=True, default=dict, null=True)),
                ('distribution', models.CharField(blank=True, max_length=100, null=True)),
                ('shift_calender', models.DateTimeField(blank=True, null=True)),
                ('pre_identified_candidate', models.BooleanField(default=False)),
                ('pre_identified_vendor', models.BooleanField(default=False)),
                ('schedule_interview', models.CharField(choices=[('No', 'No'), ('Optional', 'Optional'), ('Required', 'Required')], default='N0', max_length=50)),
                ('response_by_date', models.DateField(blank=True, null=True)),
                ('approve', models.BooleanField(db_index=True, default=True)),
                ('status', models.CharField(choices=[('Draft', 'Draft'), ('pending_approval', 'pending_approval'), ('Sourcing', 'Sourcing'), ('Rejected', 'Rejected'), ('Hold', 'Hold'), ('Filled', 'Filled'), ('Closed', 'Closed'), ('Open (Approved)', 'Open (Approved)'), ('Pending Approval - Sourcing', 'Pending Approval - Sourcing'), ('Re-open', 'Re-open'), ('Pending - PMO', 'Pending - PMO')], default='Nothing', max_length=100)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.CharField(blank=True, max_length=50, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=50, null=True)),
                ('is_template', models.BooleanField(default=False)),
                ('submit_type', models.CharField(choices=[('Draft', 'Draft'), ('Submit', 'Submit')], default='Draft', max_length=50)),
                ('is_delete', models.BooleanField(default=False)),
                ('budget_estimate', models.FloatField(blank=True, null=True)),
                ('rate', models.FloatField(blank=True, null=True)),
                ('rate_type', models.CharField(blank=True, max_length=50, null=True)),
                ('hours_per_day', models.FloatField(blank=True, null=True)),
                ('total_hours', models.FloatField(blank=True, null=True)),
                ('total_days', models.IntegerField(blank=True, null=True)),
                ('additional_amount', models.FloatField(blank=True, null=True)),
                ('adjustment_type', models.CharField(blank=True, max_length=50, null=True)),
                ('allow_expense', models.BooleanField(default=False)),
                ('assignment_length', models.FloatField(blank=True, null=True)),
                ('min_budget', models.FloatField(blank=True, null=True)),
                ('max_budget', models.FloatField(blank=True, null=True)),
                ('adjustment_value', models.CharField(blank=True, max_length=50, null=True)),
                ('trigger_approval_workflow', models.BooleanField(default=False)),
                ('unit_of_measure', models.CharField(blank=True, max_length=200, null=True)),
                ('note_for_approver', models.CharField(blank=True, max_length=200, null=True)),
                ('vendor_rate_exceed', models.BooleanField(default=False)),
                ('checklist', django_mysql.models.JSONField(blank=True, default=dict, null=True)),
                ('approverlist', django_mysql.models.JSONField(blank=True, default=dict, null=True)),
                ('check_max_bill_rate', models.BooleanField(default=False)),
                ('job_board_id', models.IntegerField(blank=True, null=True)),
                ('job_board_reference_number', models.CharField(blank=True, max_length=50, null=True)),
                ('rate_model', models.CharField(blank=True, max_length=50, null=True)),
                ('ot_exempt', models.BooleanField(default=False)),
                ('template_name', models.CharField(blank=True, max_length=200, null=True)),
                ('allow_user_description', models.BooleanField(default=False)),
                ('positions', models.CharField(blank=True, max_length=50, null=True)),
                ('direct_sourcing_distribution', models.BooleanField(default=False)),
                ('is_enabled', models.BooleanField(default=True)),
                ('submissions_from_direct_sourcing', django_mysql.models.JSONField(blank=True, default=dict, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='job_category', to='job_catalog.JobCategory')),
                ('tags', models.ManyToManyField(blank=True, related_name='job_Tags', to='job_catalog.JobTag')),
                ('template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job.Job')),
                ('title', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='job_title', to='job_catalog.JobTitle')),
            ],
            options={
                'verbose_name': 'Job',
                'verbose_name_plural': 'Jobs',
            },
        ),
        migrations.CreateModel(
            name='JobConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('program_id', models.CharField(max_length=50)),
                ('config_json', django_mysql.models.JSONField(default=dict)),
                ('is_active', models.BooleanField(default=True)),
                ('version', models.CharField(max_length=10)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Job Configuration',
                'verbose_name_plural': 'Job Configurations',
            },
        ),
        migrations.CreateModel(
            name='TalentNeuron',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate_card_id', models.IntegerField(blank=True, null=True)),
                ('hiring_difficulty', models.CharField(max_length=50)),
                ('hd_level', models.IntegerField(blank=True, null=True)),
                ('salary', models.IntegerField(blank=True, null=True)),
                ('es_market_followers', models.IntegerField(blank=True, null=True)),
                ('es_market_payers', models.IntegerField(blank=True, null=True)),
                ('es_market_leaders', models.IntegerField(blank=True, null=True)),
                ('min', models.IntegerField(blank=True, null=True)),
                ('max', models.IntegerField(blank=True, null=True)),
                ('range_min', models.IntegerField(blank=True, null=True)),
                ('range_max', models.IntegerField(blank=True, null=True)),
                ('supply', models.IntegerField(blank=True, null=True)),
                ('demand', models.IntegerField(blank=True, null=True)),
                ('posting_duration', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'TalentNeuron',
                'verbose_name_plural': 'TalentNeurons',
            },
        ),
        migrations.CreateModel(
            name='JobCustom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('program_id', models.CharField(max_length=50)),
                ('column_1', models.CharField(blank=True, max_length=255, null=True)),
                ('column_2', models.CharField(blank=True, max_length=255, null=True)),
                ('column_3', models.CharField(blank=True, max_length=255, null=True)),
                ('column_4', models.CharField(blank=True, max_length=255, null=True)),
                ('column_5', models.CharField(blank=True, max_length=255, null=True)),
                ('column_6', models.CharField(blank=True, max_length=255, null=True)),
                ('column_7', models.CharField(blank=True, max_length=255, null=True)),
                ('column_8', models.CharField(blank=True, max_length=255, null=True)),
                ('column_9', models.CharField(blank=True, max_length=255, null=True)),
                ('column_10', models.CharField(blank=True, max_length=255, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.CharField(blank=True, max_length=50, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=50, null=True)),
                ('is_delete', models.BooleanField(default=False)),
                ('job', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='custom_fields', to='job.Job')),
            ],
            options={
                'verbose_name': 'Job Custom',
                'verbose_name_plural': 'Job Customs',
            },
        ),
        migrations.CreateModel(
            name='HistoricalJobCustom',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('program_id', models.CharField(max_length=50)),
                ('column_1', models.CharField(blank=True, max_length=255, null=True)),
                ('column_2', models.CharField(blank=True, max_length=255, null=True)),
                ('column_3', models.CharField(blank=True, max_length=255, null=True)),
                ('column_4', models.CharField(blank=True, max_length=255, null=True)),
                ('column_5', models.CharField(blank=True, max_length=255, null=True)),
                ('column_6', models.CharField(blank=True, max_length=255, null=True)),
                ('column_7', models.CharField(blank=True, max_length=255, null=True)),
                ('column_8', models.CharField(blank=True, max_length=255, null=True)),
                ('column_9', models.CharField(blank=True, max_length=255, null=True)),
                ('column_10', models.CharField(blank=True, max_length=255, null=True)),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('modified_on', models.DateTimeField(blank=True, editable=False)),
                ('created_by', models.CharField(blank=True, max_length=50, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=50, null=True)),
                ('is_delete', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('job', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='job.Job')),
            ],
            options={
                'verbose_name': 'historical Job Custom',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalJob',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('uid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('job_manager', models.CharField(blank=True, max_length=50, null=True)),
                ('msp_manager', models.CharField(blank=True, max_length=50, null=True)),
                ('program_id', models.CharField(blank=True, db_index=True, max_length=50, null=True)),
                ('type', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('hire_type', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('company_name', models.CharField(blank=True, db_index=True, max_length=200, null=True)),
                ('level', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('no_of_openings', models.IntegerField(blank=True, null=True)),
                ('location_id', models.CharField(blank=True, db_index=True, default=0, max_length=100, null=True)),
                ('salary_min_range', models.IntegerField(blank=True, null=True)),
                ('salary_max_range', models.IntegerField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('start_date', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('hierarchy', models.CharField(blank=True, max_length=256, null=True)),
                ('hierarchy_location', models.CharField(blank=True, max_length=256, null=True)),
                ('currency', models.CharField(blank=True, max_length=200, null=True)),
                ('min_bill_rate', models.FloatField(blank=True, null=True)),
                ('max_bill_rate', models.FloatField(blank=True, null=True)),
                ('shift', models.CharField(blank=True, max_length=100, null=True)),
                ('qualifications', django_mysql.models.JSONField(blank=True, default=dict, null=True)),
                ('distribution', models.CharField(blank=True, max_length=100, null=True)),
                ('shift_calender', models.DateTimeField(blank=True, null=True)),
                ('pre_identified_candidate', models.BooleanField(default=False)),
                ('pre_identified_vendor', models.BooleanField(default=False)),
                ('schedule_interview', models.CharField(choices=[('No', 'No'), ('Optional', 'Optional'), ('Required', 'Required')], default='N0', max_length=50)),
                ('response_by_date', models.DateField(blank=True, null=True)),
                ('approve', models.BooleanField(db_index=True, default=True)),
                ('status', models.CharField(choices=[('Draft', 'Draft'), ('pending_approval', 'pending_approval'), ('Sourcing', 'Sourcing'), ('Rejected', 'Rejected'), ('Hold', 'Hold'), ('Filled', 'Filled'), ('Closed', 'Closed'), ('Open (Approved)', 'Open (Approved)'), ('Pending Approval - Sourcing', 'Pending Approval - Sourcing'), ('Re-open', 'Re-open'), ('Pending - PMO', 'Pending - PMO')], default='Nothing', max_length=100)),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('modified_on', models.DateTimeField(blank=True, editable=False)),
                ('created_by', models.CharField(blank=True, max_length=50, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=50, null=True)),
                ('is_template', models.BooleanField(default=False)),
                ('submit_type', models.CharField(choices=[('Draft', 'Draft'), ('Submit', 'Submit')], default='Draft', max_length=50)),
                ('is_delete', models.BooleanField(default=False)),
                ('budget_estimate', models.FloatField(blank=True, null=True)),
                ('rate', models.FloatField(blank=True, null=True)),
                ('rate_type', models.CharField(blank=True, max_length=50, null=True)),
                ('hours_per_day', models.FloatField(blank=True, null=True)),
                ('total_hours', models.FloatField(blank=True, null=True)),
                ('total_days', models.IntegerField(blank=True, null=True)),
                ('additional_amount', models.FloatField(blank=True, null=True)),
                ('adjustment_type', models.CharField(blank=True, max_length=50, null=True)),
                ('allow_expense', models.BooleanField(default=False)),
                ('assignment_length', models.FloatField(blank=True, null=True)),
                ('min_budget', models.FloatField(blank=True, null=True)),
                ('max_budget', models.FloatField(blank=True, null=True)),
                ('adjustment_value', models.CharField(blank=True, max_length=50, null=True)),
                ('trigger_approval_workflow', models.BooleanField(default=False)),
                ('unit_of_measure', models.CharField(blank=True, max_length=200, null=True)),
                ('note_for_approver', models.CharField(blank=True, max_length=200, null=True)),
                ('vendor_rate_exceed', models.BooleanField(default=False)),
                ('checklist', django_mysql.models.JSONField(blank=True, default=dict, null=True)),
                ('approverlist', django_mysql.models.JSONField(blank=True, default=dict, null=True)),
                ('check_max_bill_rate', models.BooleanField(default=False)),
                ('job_board_id', models.IntegerField(blank=True, null=True)),
                ('job_board_reference_number', models.CharField(blank=True, max_length=50, null=True)),
                ('rate_model', models.CharField(blank=True, max_length=50, null=True)),
                ('ot_exempt', models.BooleanField(default=False)),
                ('template_name', models.CharField(blank=True, max_length=200, null=True)),
                ('allow_user_description', models.BooleanField(default=False)),
                ('positions', models.CharField(blank=True, max_length=50, null=True)),
                ('direct_sourcing_distribution', models.BooleanField(default=False)),
                ('is_enabled', models.BooleanField(default=True)),
                ('submissions_from_direct_sourcing', django_mysql.models.JSONField(blank=True, default=dict, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('category', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='job_catalog.JobCategory')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('template', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='job.Job')),
                ('title', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='job_catalog.JobTitle')),
            ],
            options={
                'verbose_name': 'historical Job',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='FoundationQualificationData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('program_id', models.CharField(blank=True, max_length=50, null=True)),
                ('entity_id', models.CharField(blank=True, max_length=50, null=True)),
                ('entity_type', models.CharField(blank=True, max_length=50, null=True)),
                ('entity_name', models.CharField(blank=True, max_length=50, null=True)),
                ('entity_key', models.CharField(blank=True, max_length=50, null=True)),
                ('entity_value', models.CharField(blank=True, max_length=50, null=True)),
                ('entity_is_active', models.BooleanField(default=False)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foundation_fields', to='job.Job')),
            ],
        ),
    ]
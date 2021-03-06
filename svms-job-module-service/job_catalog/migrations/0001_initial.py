# Generated by Django 3.0.8 on 2021-01-01 16:50

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('naics_code', models.CharField(db_index=True, max_length=100, unique=True)),
                ('industry_type', models.CharField(max_length=1000)),
            ],
            options={
                'verbose_name': 'Industry',
                'verbose_name_plural': 'Industries',
                'unique_together': {('naics_code', 'industry_type')},
            },
        ),
        migrations.CreateModel(
            name='JobCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('o_net_soc_code', models.CharField(db_index=True, max_length=30, unique=True)),
                ('category_name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name': 'Job Category',
                'verbose_name_plural': 'Job Categories',
                'unique_together': {('o_net_soc_code', 'category_name')},
            },
        ),
        migrations.CreateModel(
            name='JobTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(db_index=True, max_length=100)),
            ],
            options={
                'verbose_name': 'Job Tag',
                'verbose_name_plural': 'Job Tags',
            },
        ),
        migrations.CreateModel(
            name='JobCatalog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='job_catalog', to='job_catalog.JobCategory', to_field='o_net_soc_code')),
                ('naics_code', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='job_catalog', to='job_catalog.Industry', to_field='naics_code')),
            ],
            options={
                'verbose_name': 'Job Catalog',
                'verbose_name_plural': 'Job Catalogs',
            },
        ),
        migrations.CreateModel(
            name='JobTitle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('program_id', models.CharField(db_index=True, max_length=100)),
                ('title', models.CharField(db_index=True, max_length=100)),
                ('level', models.IntegerField()),
                ('description', models.TextField()),
                ('status', models.BooleanField(default=True)),
                ('created_by', models.CharField(max_length=100)),
                ('modified_by', models.CharField(max_length=100)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='job_title', to='job_catalog.JobCategory', to_field='o_net_soc_code')),
                ('job_tag', models.ManyToManyField(blank=True, related_name='job_title', to='job_catalog.JobTag')),
            ],
            options={
                'verbose_name': 'Job Title',
                'verbose_name_plural': 'Job Titles',
                'unique_together': {('program_id', 'category', 'title')},
            },
        ),
    ]

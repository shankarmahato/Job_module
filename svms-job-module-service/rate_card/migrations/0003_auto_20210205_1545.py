# Generated by Django 3.0.8 on 2021-02-05 10:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rate_card', '0002_ratecardconfig'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ratecard',
            name='max_rate',
        ),
        migrations.RemoveField(
            model_name='ratecard',
            name='max_rate_rule',
        ),
        migrations.RemoveField(
            model_name='ratecard',
            name='min_rate',
        ),
        migrations.RemoveField(
            model_name='ratecard',
            name='min_rate_rule',
        ),
        migrations.RemoveField(
            model_name='ratecard',
            name='unit_of_measure',
        ),
        migrations.CreateModel(
            name='RatesOfRateCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_of_measure', models.CharField(blank=True, max_length=200, null=True)),
                ('min_rate', models.FloatField(blank=True, null=True)),
                ('max_rate', models.FloatField(blank=True, null=True)),
                ('min_rate_rule', models.CharField(choices=[('Can Change', 'Can Change'), ('Cannot Reduce', 'Cannot Reduce'), ('Cannot Change', 'Cannot Change')], default='Can Change', max_length=100)),
                ('max_rate_rule', models.CharField(choices=[('Can Change', 'Can Change'), ('Cannot Reduce', 'Cannot Reduce'), ('Cannot Change', 'Cannot Change')], default='Can Change', max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('rate_card', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='rates_of_rate_card', to='rate_card.RateCard')),
            ],
            options={
                'verbose_name': 'Rate',
                'verbose_name_plural': 'Rates',
            },
        ),
    ]

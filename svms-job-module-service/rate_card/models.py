import uuid

from django.db import models
from django_mysql.models import JSONField

rate_rule = (
    ("Can Change", "Can Change"),
    ("Cannot Reduce", "Cannot Reduce"),
    ("Cannot Change", "Cannot Change")
)


class RateCardConfig(models.Model):
    program_id = models.UUIDField(db_index=True, unique=True)
    config_json = JSONField(default=dict)

    def __str__(self):
        reference_str = "{}".format(self.program_id)
        return reference_str.title()

    class Meta:
        verbose_name = 'Rate Card Config'
        verbose_name_plural = 'Rate Cards Config'


class RateCard(models.Model):
    """ model for Rate Card """

    uid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True)
    program_id = models.CharField(max_length=100, db_index=True)
    job_category = models.ForeignKey(
        "job_catalog.JobCategory", related_name="rate_card",
        on_delete=models.DO_NOTHING)
    job_title = models.ForeignKey(
        "job_catalog.JobTitle", related_name="rate_card",
        on_delete=models.DO_NOTHING)
    job_level = models.IntegerField()
    job_template = models.ForeignKey(
        "job.Job", related_name="rate_card", on_delete=models.DO_NOTHING,
        blank=True, null=True)
    hierarchy = models.CharField(max_length=100, null=True, blank=True)
    # foundational_data_type = models.ForeignKey(
    #     "job.FoundationData", related_name="rate_card",
    #     on_delete=models.DO_NOTHING, null=True, blank=True)
    work_location = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    currency = models.CharField(max_length=100)

    def __str__(self):
        reference_str = "{}_{}_{}".format(
            self.job_category, self.job_title, self.job_level)
        return reference_str.title()

    class Meta:
        verbose_name = 'Rate Card'
        verbose_name_plural = 'Rate Cards'
        unique_together = (
            'program_id', 'job_category', 'job_title', 'job_level',
            'job_template',
            'hierarchy', 'work_location', 'region', 'currency')


class RatesOfRateCard(models.Model):
    """
    rates of RateCard
    """
    rate_card = models.ForeignKey(RateCard, related_name="rates_of_rate_card",
                                  on_delete=models.DO_NOTHING)
    unit_of_measure = models.CharField(max_length=200, null=True, blank=True)
    min_rate = models.FloatField(null=True, blank=True)
    max_rate = models.FloatField(null=True, blank=True)
    min_rate_rule = models.CharField(
        max_length=100, choices=rate_rule, default="Can Change")
    max_rate_rule = models.CharField(
        max_length=100, choices=rate_rule, default="Can Change")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        reference_str = "{}_{}_{}_{}".format(self.rate_card,
                                             self.unit_of_measure,
                                             self.min_rate, self.max_rate)
        return reference_str.title()

    class Meta:
        verbose_name = 'Rate'
        verbose_name_plural = 'Rates'
        unique_together = (
            ("rate_card_id", "unit_of_measure"),
        )

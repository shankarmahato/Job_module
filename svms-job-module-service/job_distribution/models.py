import datetime
import uuid

from django.db import models

distribute_method_choice = (
    ("on_submit", "On Submit"),
    ("final_approval", "Final Approval")
)

distribute_type_choice = (
    ("manual", "Manual"),
    ("automatic", "Automatic"),
    ("scheduled", "Scheduled")
)

scedule_status_choice = (
    ("scheduling", "scheduling"),
    ("distributed", "distributed"),

)

vendor_selection_choice = (
    ("industry_region", "Industry/Region"),
    ("manual_input", "Manual Input")
)

opt_option = (
    ("no_response", "No Response"),
    ("opt_in", "Opt In"),
    ("opt_out", "Opt Out")
)

opt_out_reasons = (
    ("", ""),
    ("Cannot Service This Category", "Cannot Service This Category"),
    ("Cannot Service This Location", "Cannot Service This Location"),
    ("Cannot Service This Position", "Cannot Service This Position"),
    ("No Qualified Candidates Available", "No Qualified Candidates Available"),
    ("Supplier can later come back and opt-in for the opted-out job",
     "Supplier can later come back and opt-in for the opted-out job")
)


class ScheduleJobVendorMapping(models.Model):
    uid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True)
    program_id = models.CharField(max_length=100, db_index=True)
    job = models.ForeignKey(
        "job.Job", related_name="schedule_job_vendor_mapping",
        on_delete=models.DO_NOTHING)
    distribute_type = models.CharField(
        max_length=100, choices=distribute_type_choice, default='scheduled')
    vendor_id = models.CharField(
        max_length=100, db_index=True, blank=True, null=True)
    vendor_group_id = models.CharField(
        max_length=100, db_index=True, blank=True, null=True)
    distribution_id = models.CharField(max_length=100, blank=True, null=True)
    scheduled_datetime = models.DateTimeField(
        verbose_name="Scheduled datetime", null=True)
    scheduled_status = models.CharField(
        max_length=100, choices=scedule_status_choice, default='scheduling')
    submission_limit = models.IntegerField(blank=True, null=True)
    created_on = models.DateTimeField(default=datetime.datetime.now)
    modified_on = models.DateTimeField(
        auto_now=True, blank=True)
    created_by = models.CharField(max_length=36, null=True, blank=True)
    modified_by = models.CharField(max_length=36, null=True, blank=True)

    def __str__(self):
        return "{}_{}_{}_{}".format(
            self.vendor_id,
            self.program_id,
            self.job,
            self.distribute_type
        )


class VendorJobMapping(models.Model):
    """
    Vendor Job Mapping Table
    """
    uid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True)
    program_id = models.CharField(max_length=100, db_index=True)
    job = models.ForeignKey(
        "job.Job", related_name="vendor_job_mapping",
        on_delete=models.DO_NOTHING)
    distribute_type = models.CharField(
        max_length=100, choices=distribute_type_choice, default='manual')
    vendor_id = models.CharField(
        max_length=100, db_index=True, blank=True, null=True)
    vendor_group_id = models.CharField(
        max_length=100, db_index=True, blank=True, null=True)
    distribution_id = models.CharField(max_length=100, blank=True, null=True)
    distribute_method = models.CharField(
        max_length=100, choices=distribute_method_choice, blank=True, null=True)
    vendor_selection = models.CharField(
        max_length=100, choices=vendor_selection_choice, blank=True, null=True)
    opt_option = models.CharField(
        max_length=100, choices=opt_option, default="no_response")
    submission_limit = models.IntegerField(blank=True, null=True)
    reason = models.CharField(max_length=100, blank=True, null=True,
                              choices=opt_out_reasons, default="")
    created_on = models.DateTimeField(default=datetime.datetime.now)
    modified_on = models.DateTimeField(
        auto_now=True, blank=True)
    created_by = models.CharField(max_length=36, null=True, blank=True)
    modified_by = models.CharField(max_length=36, null=True, blank=True)

    class Meta:
        verbose_name = 'VendorJobMapping'
        verbose_name_plural = 'VendorJobMappings'
        # unique_together = ('program_id', 'job_id', 'distribute_type')

    def __str__(self):
        return "{}_{}_{}_{}".format(
            self.vendor_id,
            self.program_id,
            self.job,
            self.distribute_type
        )

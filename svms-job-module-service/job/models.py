from django.db import models, transaction, OperationalError
from django.contrib.auth.models import User
from django_mysql.models import JSONField
from simple_history.models import HistoricalRecords
from job_catalog.models import JobCategory,JobTitle,JobTag,Industry
import uuid
from django.db.models import signals
from django.dispatch import receiver
# Create your models here.



class FoundationData(models.Model):
    """ User define foundation  info """
    program_id = models.CharField(max_length=50)
    cost_center = models.CharField(max_length=255,null=True,blank=True)
    company_code = models.CharField(max_length=255,null=True,blank=True)
    gl_code = models.CharField(max_length=255,null=True,blank=True)
    source_code = models.CharField(max_length=255,null=True,blank=True)
    market_region = models.CharField(max_length=255,null=True,blank=True)
    work_location = models.CharField(max_length=255,null=True,blank=True)
    status = models.BooleanField(default=True,db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=50,null=True,blank=True)
    modified_by = models.CharField(max_length=50,null=True,blank=True)

    def __str__(self):
        return self.cost_center

    class Meta:
        verbose_name = 'Foundation Data'
        verbose_name_plural = 'Foundation Data'



class JobConfiguration(models.Model):
    """ defining json configuration model """
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    program_id = models.CharField(max_length=50)
    config_json = JSONField()
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=10)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Job Configuration'
        verbose_name_plural = 'Job Configurations'


job_source = (
    ('Template',"Template"),
    ('CopyJob',"CopyJob"),
    ('Catalog',"Catalog")
    )
schedule_interview_choices=(
    ("No","No"),
    ("Optional","Optional"),
    ("Required","Required")
    )
submit_type_choices = (
    ('Draft',"Draft"),
    ('Submit',"Submit")
    )
status_type_choices = (
    ("Draft","Draft"),
    ("pending_approval","pending_approval"),
    ("Sourcing","Sourcing"),
    ("Rejected","Rejected"),
    ("Hold","Hold"),
    ("Filled","Filled"),
    ("Closed","Closed"),
    ("Open (Approved)","Open (Approved)"),
    ("Pending Approval - Sourcing","Pending Approval - Sourcing"),
    ("Re-open","Re-open"),
    ("Pending - PMO","Pending - PMO")
)
class Job(models.Model):
    """ defining jobs with system and custom columns"""
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    job_manager =models.CharField(max_length=50,null=True,blank=True)
    msp_manager = models.CharField(max_length=50,null=True,blank=True) 
    program_id = models.CharField(max_length=50,blank=True,null=True, db_index=True)
    category = models.ForeignKey(JobCategory,related_name='job_category',on_delete=models.DO_NOTHING)
    title = models.ForeignKey(JobTitle,related_name='job_title',on_delete=models.DO_NOTHING)    
    type = models.CharField(max_length=100,db_index=True,null=True,blank=True)
    hire_type = models.CharField(max_length=100,db_index=True,null=True,blank=True)
    company_name = models.CharField(max_length=200,db_index=True, null=True,blank=True)
    level = models.CharField(max_length=100,db_index=True,null=True,blank=True)
    no_of_openings = models.IntegerField(null=True,blank=True)
    location_id = models.CharField(max_length=100,db_index=True,null=True,blank=True,default=0)
    salary_min_range = models.IntegerField(null=True,blank=True)
    salary_max_range = models.IntegerField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    start_date = models.DateTimeField(db_index=True,null=True,blank=True)
    end_date = models.DateTimeField(db_index=True,null=True,blank=True)
    tags = models.ManyToManyField(JobTag,related_name='job_Tags', blank=True)
    hierarchy = models.CharField(max_length=256,null=True,blank=True)
    hierarchy_location = models.CharField(max_length=256,null=True,blank=True)
    currency = models.CharField(max_length=200,null=True,blank=True)
    min_bill_rate = models.FloatField(null=True,blank=True)
    max_bill_rate = models.FloatField(null=True,blank=True)
    shift = models.CharField(max_length=100,null=True,blank=True)
    qualifications = JSONField(null=True,blank=True)
    distribution = models.CharField(max_length=100,null=True,blank=True)
    shift_calender = models.DateTimeField(null=True,blank=True)
    pre_identified_candidate= models.BooleanField(default=False)
    pre_identified_vendor= models.BooleanField(default=False)
    schedule_interview=models.CharField(max_length=50,choices = schedule_interview_choices, default ='N0')
    response_by_date = models.DateField(null=True,blank=True)
    approve = models.BooleanField(default=True,db_index=True)
    status = models.CharField(max_length=100,choices = status_type_choices,default ='Nothing')
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=50,null=True,blank=True)
    modified_by = models.CharField(max_length=50,null=True,blank=True)
    template = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True)
    is_template = models.BooleanField(default=False)
    submit_type = models.CharField(max_length=50,choices = submit_type_choices, default ='Draft')
    is_delete = models.BooleanField(default=False)
    budget_estimate = models.FloatField(null=True,blank=True)	
    rate = models.FloatField(null=True,blank=True)
    rate_type = models.CharField(max_length=50,null=True,blank=True)
    hours_per_day = models.FloatField(null=True,blank=True)
    total_hours = models.FloatField(null=True,blank=True)
    total_days = models.IntegerField(null=True,blank=True)
    additional_amount = models.FloatField(null=True,blank=True)
    adjustment_type =  models.CharField(max_length=50,null=True,blank=True)
    allow_expense =   models.BooleanField(default=False)
    assignment_length =  models.FloatField(null=True,blank=True)
    min_budget =  models.FloatField(null=True,blank=True)
    max_budget =  models.FloatField(null=True,blank=True)
    adjustment_value =  models.CharField(max_length=50,null=True,blank=True)
    trigger_approval_workflow = models.BooleanField(default=False)
    unit_of_measure = models.CharField(max_length=200,null=True,blank=True)
    note_for_approver = models.CharField(max_length=200,null=True,blank=True)
    vendor_rate_exceed = models.BooleanField(default=False)
    checklist = JSONField(null=True,blank=True)
    approverlist = JSONField(null=True,blank=True)
    check_max_bill_rate = models.BooleanField(default=False)
    job_board_id = models.IntegerField(null=True,blank=True)
    job_board_reference_number = models.CharField(max_length=50,null=True,blank=True)
    rate_model = models.CharField(max_length=50,null=True,blank=True)
    ot_exempt = models.BooleanField(default=False)
    template_name = models.CharField(max_length=200,null=True,blank=True)
    allow_user_description = models.BooleanField(default=False)
    positions = models.CharField(max_length=50,null=True,blank=True)
    direct_sourcing_distribution = models.BooleanField(default=False)
    is_enabled = models.BooleanField(default=True)
    submissions_from_direct_sourcing = JSONField(null=True,blank=True)
    automatic_distribution =models.BooleanField(default=False)
    submission_limit_vendor = models.IntegerField(null=True,blank=True)
    automatic_distribute_submit = models.BooleanField(default=False)
    automatic_distribute_final_approval = models.BooleanField(default=False)
    tiered_distribute_schedule=models.BooleanField(default=False)
    distribute_schedule = models.CharField(max_length=200,null=True,blank=True)
    immediate_distribution = JSONField(null=True,blank=True)
    after_immediate_distribution = JSONField(null=True,blank=True)
    manual_distribution_job_submit = models.BooleanField(default=False)
    submission_exceed_max_bill_rate = models.BooleanField(default=False)
    source = models.CharField(max_length=100,choices = job_source,default ='Nothing')
    source_id = models.CharField(max_length=200,null=True,blank=True)
    job_id = models.CharField(max_length=50,null=True,blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.title.title+"-"+str(self.uid)

    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['id']

class JobCustom(models.Model):
    """define job custom columns"""
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    program_id = models.CharField(max_length=50)
    job = models.OneToOneField(Job,on_delete=models.CASCADE,related_name="custom_fields")
    column_1 = models.CharField(max_length=255,null=True,blank=True)
    column_2 = models.CharField(max_length=255,null=True,blank=True)
    column_3 = models.CharField(max_length=255,null=True,blank=True)
    column_4 = models.CharField(max_length=255,null=True,blank=True)
    column_5 = models.CharField(max_length=255,null=True,blank=True)
    column_6 = models.CharField(max_length=255,null=True,blank=True)
    column_7 = models.CharField(max_length=255,null=True,blank=True)
    column_8 = models.CharField(max_length=255,null=True,blank=True)
    column_9 = models.CharField(max_length=255,null=True,blank=True)
    column_10 = models.CharField(max_length=255,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=50,null=True,blank=True)
    modified_by = models.CharField(max_length=50,null=True,blank=True)
    is_delete = models.BooleanField(default=False)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Job Custom'
        verbose_name_plural = 'Job Customs'

    def __str__(self):
        return self.job.title.title



class TalentNeuron(models.Model):
    """ Talent Neuron Model """
    rate_card_id  = models.IntegerField(null=True,blank=True)
    hiring_difficulty = models.CharField(max_length=50)
    hd_level  = models.IntegerField(null=True,blank=True)
    salary = models.IntegerField(null=True,blank=True)
    es_market_followers = models.IntegerField(null=True,blank=True)
    es_market_payers = models.IntegerField(null=True,blank=True)
    es_market_leaders = models.IntegerField(null=True,blank=True)
    min = models.IntegerField(null=True,blank=True)
    max = models.IntegerField(null=True,blank=True)
    range_min = models.IntegerField(null=True,blank=True)
    range_max = models.IntegerField(null=True,blank=True)
    supply = models.IntegerField(null=True,blank=True)
    demand = models.IntegerField(null=True,blank=True)
    posting_duration = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(null=True,blank=True)

    class Meta:
        verbose_name = 'TalentNeuron'
        verbose_name_plural = 'TalentNeurons'



class FoundationQualificationData(models.Model):
    """define foundation data with qualification"""
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    program_id = models.CharField(max_length=50,null=True,blank=True)
    job= models.ForeignKey(Job,on_delete=models.CASCADE,related_name="foundation_fields")
    entity_id = models.CharField(max_length=50, null=True, blank=True)
    entity_type = models.CharField(max_length=50,null=True,blank=True)
    entity_name = models.CharField(max_length=50,null=True,blank=True)
    entity_key = models.CharField(max_length=50,null=True,blank=True)
    entity_value = models.CharField(max_length=50,null=True,blank=True)
    entity_is_active = models.BooleanField(default=False)


    def __str__(self):
        return self.entity_name

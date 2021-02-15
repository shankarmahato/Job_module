from rest_framework import serializers
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from job.models import Job,JobCustom,JobConfiguration,FoundationData,TalentNeuron,FoundationQualificationData
from connectors.vms_profile_manager.serializers import RemoteUserInfoSerializer
from job_catalog.serializers import JobTitleSerializer, CategorySerializer,JobTagSerializer,CategoryListSerializer,JobTitleListSerializer
from job_catalog.models import JobCategory,JobTitle,JobTag
from job.external_api import ConfiguratorService
import collections
import requests

import json
logger = settings.LOGGER


class JobSerializer(serializers.ModelSerializer):
    """Create Job """

    category = serializers.PrimaryKeyRelatedField(queryset=JobCategory.objects.all(),
        required=True,
        
        write_only=False)
    title = serializers.PrimaryKeyRelatedField(queryset=JobTitle.objects.all(),
        required=True,
        
        write_only=False)
    tags = serializers.PrimaryKeyRelatedField(queryset=JobTag.objects.all(),many=True, required=True)
    
    class Meta:
        model= Job
        fields = '__all__'

class CustomSerializer(RemoteUserInfoSerializer):
    """ Custom column mapping """
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all(),
        required=True,
        
        write_only=False)
    

    class Meta:
        model = JobCustom
        fields = '__all__'

    def create(self, validated_data):
        #validated_data["config_id"] = validated_data["job"].config_id
        job_custom = JobCustom.objects.create(**validated_data)
        return job_custom

    def update(self, instance, validated_data):
        # if 'job' in validated_data:
        #     Job.objects.filter(pk=instance.pk).update(**validated_data['job'])
        #     del validated_data['job']
        JobCustom.objects.filter(job=instance.job).update(**validated_data)
        return instance


class FoundationData(serializers.ModelSerializer):
    """ user define foundation data serializer """
    class Meta:
        model=FoundationData
        fields = ('id','cost_center','company_code','gl_code','source_code','market_region','work_location')

class ConfigurationSerializer(serializers.ModelSerializer):
    """ configuration of json """
    class Meta:
        model = JobConfiguration
        fields = '__all__'


class JobTemplateSerializer(serializers.ModelSerializer):
    """ define Job Serializer"""

    category = serializers.PrimaryKeyRelatedField(queryset=JobCategory.objects.all(),
        required=True,
        
        write_only=False)
    title = serializers.PrimaryKeyRelatedField(queryset=JobTitle.objects.all(),
        required=True,
        
        write_only=False)
    
    class Meta:
        model= Job
        # fields = '__all__'
        fields = ('id','uid','program_id','job_manager','msp_manager','title','category','type','hire_type','company_name','level','no_of_openings',
        'rate', 'rate_type','hours_per_day','total_hours','total_days','additional_amount','adjustment_type',
        'allow_expense','assignment_length','min_budget','max_budget','adjustment_value',
        'location_id','description','start_date','end_date','hierarchy','hierarchy_location','budget_estimate','currency','min_bill_rate','max_bill_rate','shift','distribution','shift_calender','pre_identified_candidate','pre_identified_vendor','schedule_interview',
            'response_by_date','approve','is_template','template_name','tags','qualifications',
                 'created_by','modified_by','is_delete','status','checklist','trigger_approval_workflow','unit_of_measure','submissions_from_direct_sourcing','automatic_distribution','submission_limit_vendor','automatic_distribute_submit','automatic_distribute_final_approval','tiered_distribute_schedule','distribute_schedule',
                  'immediate_distribution','after_immediate_distribution','manual_distribution_job_submit','submission_exceed_max_bill_rate',
                  'note_for_approver','vendor_rate_exceed','approverlist','job_board_id','job_board_reference_number','check_max_bill_rate','rate_model','ot_exempt','allow_user_description','positions','direct_sourcing_distribution','is_enabled','submissions_from_direct_sourcing'
                  )



class TalentNeuronSerializer(serializers.ModelSerializer):

    class Meta:
        model = TalentNeuron
        fields = '__all__'

import collections

from django.conf import settings
from rest_framework import serializers

from connectors.vms_profile_manager.helpers import RemoteUserDataHandler
from connectors.vms_profile_manager.serializers import RemoteUserInfoSerializer
from job.models import Job
# from job.serializers import JobListSerializer
from job_catalog.serializers import JobTitleSerializer, JobCategorySerializer, \
    JobTagSerializer
from rate_card.serializers import RateCardJobTemplateSerializer
from .config import get_vendor_details, get_vendor_submitted_candidates
from .models import VendorJobMapping, opt_option, ScheduleJobVendorMapping, \
    opt_out_reasons
from .utils import get_location_details


# class JobSerializer(serializers.ModelSerializer):
#     """
#     serializer for Job Serializer
#     """

#     class Meta:
#         """
#         Meta class for Job Serializer
#         """
#         model = Job
#         fields = (
#             'id',
#             'title',
#         )
#         read_only_fields = (
#             'id',
#             'title',
#         )

class VendorGroupIdSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    vendor_id = serializers.ListField(
        child=serializers.UUIDField(), required=False)


class SchedulesSerializer(serializers.Serializer):
    schedule_unit = serializers.CharField()
    schedule_value = serializers.CharField(required=False)
    vendors = serializers.ListField(
        child=serializers.UUIDField(), required=False)
    vendor_group_id = serializers.ListField(
        child=serializers.UUIDField(), required=False)


class DistributeMethodSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    schedules = SchedulesSerializer(many=True)


class VendorJobMappingSerializerv2(serializers.ModelSerializer):
    program_id = serializers.UUIDField(required=False, write_only=True)
    job = RateCardJobTemplateSerializer(many=False, read_only=True)
    job_id = serializers.UUIDField(required=False, write_only=True)
    vendors = serializers.ListField(
        child=serializers.UUIDField(), required=False)
    vendor_id = serializers.UUIDField(required=False)
    vendor_group_id = serializers.ListField(
        child=serializers.UUIDField(), required=False)
    distribution_id = DistributeMethodSerializer(many=True, required=False)
    submission_limit = serializers.IntegerField(required=False)

    class Meta:
        """
        Meta class for Job Serializer
        """
        model = VendorJobMapping
        fields = (
            'program_id',
            'job',
            'job_id',
            'vendors',
            'vendor_group_id',
            'distribution_id',
            'distribute_type',
            'vendor_id',
            'distribute_method',
            'vendor_selection',
            'opt_option',
            'submission_limit'
        )


class JobListSerializerV2(RemoteUserInfoSerializer):
    title = JobTitleSerializer(many=False, read_only=True)
    category = JobCategorySerializer(many=False, read_only=True)
    tags = JobTagSerializer(many=True, read_only=True)
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    location_id = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = (
            'id', 'uid', 'job_manager', 'msp_manager',
            'title', 'category', 'type', 'hire_type',
            'company_name', 'level', 'no_of_openings',
            'rate', 'rate_type', 'hours_per_day', 'total_hours',
            'total_days', 'additional_amount', 'adjustment_type',
            'allow_expense', 'assignment_length', 'min_budget',
            'max_budget', 'adjustment_value',
            'location_id', 'description', 'start_date', 'end_date',
            'hierarchy', 'hierarchy_location', 'budget_estimate',
            'currency', 'min_bill_rate', 'max_bill_rate', 'shift',
            'distribution', 'shift_calender', 'pre_identified_candidate',
            'pre_identified_vendor', 'schedule_interview',
            'response_by_date', 'approve', 'is_template',
            'template', 'qualifications', 'tags', 'qualifications',
            'created_by',
            'modified_by', 'is_delete', 'status')  # 'candidate'

    def get_start_date(self, obj):
        return obj.start_date.strftime("%Y-%m-%d %H:%M:%S+00:00")

    def get_end_date(self, obj):
        return obj.end_date.strftime("%Y-%m-%d %H:%M:%S+00:00")

    def get_location_id(self, obj):
        return get_location_details(self.context.get("request"), obj.program_id,
                                    obj.location_id)


class VendorJobMappingSerializer(serializers.ModelSerializer):
    uid = serializers.UUIDField(required=False, write_only=True)
    program_id = serializers.UUIDField(required=False, write_only=True)
    job = JobListSerializerV2(many=False, read_only=True)
    job_id = serializers.UUIDField(required=False, write_only=True)
    distribution_id = serializers.CharField(required=False)
    distribute_method = serializers.CharField(required=False)
    vendor_selection = serializers.CharField(required=False)
    vendor_id = serializers.UUIDField(required=False)
    vendor = serializers.SerializerMethodField(required=False, read_only=True)
    vendor_group_id = serializers.UUIDField(required=False)
    submission_limit = serializers.IntegerField(required=False)
    created_by = serializers.SerializerMethodField()
    modified_by = serializers.SerializerMethodField()
    reason = serializers.CharField(required=False)
    submissions = serializers.SerializerMethodField(read_only=True)
    created_on = serializers.SerializerMethodField()
    modified_on = serializers.SerializerMethodField()

    class Meta:
        """
        Meta class for Job Serializer
        """
        model = VendorJobMapping
        fields = "__all__"

    def create(self, validated_data):

        job_uid = validated_data.get("job_id")

        job_obj = Job.objects.filter(uid=job_uid)

        if not job_obj:
            raise serializers.ValidationError("Valid Job id is reqired")

        job_id = job_obj[0].id
        submission_limit_vendor = job_obj[0].submission_limit_vendor

        validated_data.update({"job_id": job_id})

        submission_limit = validated_data.get("submission_limit", 0)
        reason = validated_data.get("reason", None)

        if submission_limit is not None:
            program_id = self.context["request"].data['program_id']
            job_uid = job_obj[0].uid
            vendor_id = validated_data.get("vendor_id")
            result = get_vendor_submitted_candidates(
                self.context["request"], program_id, job_uid, vendor_id)

            if submission_limit < result["total_records"]:
                submission_limit = result["total_records"]

            if submission_limit_vendor is not None:
                if result["total_records"] > submission_limit_vendor:
                    submission_limit = result["total_records"]

        vendor_job_obj, is_created = VendorJobMapping.objects.get_or_create(
            program_id=program_id,
            job_id=job_id,
            vendor_id=validated_data.get("vendor_id"))

        if is_created:
            vendor_job_obj.distribute_type = validated_data.get(
                "distribute_type")
            vendor_job_obj.vendor_group_id = validated_data.get(
                "vendor_group_id")
            vendor_job_obj.distribution_id = validated_data.get(
                "distribution_id")
            vendor_job_obj.distribute_method = validated_data.get(
                "distribute_method")
            vendor_job_obj.vendor_selection = validated_data.get(
                "vendor_selection")
            vendor_job_obj.submission_limit = submission_limit
            vendor_job_obj.reason = reason
            user_id = self.context["user_id"]
            vendor_job_obj.created_by = user_id
            vendor_job_obj.modified_by = user_id
            vendor_job_obj.save()

        if validated_data.get("distribute_type") == "scheduled":
            ScheduleJobVendorMapping.objects.filter(
                **validated_data).update(scheduled_status="distributed")
        return vendor_job_obj

    def update(self, instance, validated_data):
        program_id = validated_data.get(
            'program_id', instance.program_id)

        job_uid = validated_data.get("job_id")

        if job_uid:
            job_obj = Job.objects.filter(uid=job_uid)

            if not job_obj:
                raise serializers.ValidationError("Valid Job id is reqired")

            job_id = job_obj[0].id
            submission_limit_vendor = job_obj[0].submission_limit_vendor

        else:
            job_id = instance.job_id
            job_uid = instance.job.uid
            submission_limit_vendor = instance.job.submission_limit_vendor

        distribute_type = validated_data.get(
            'distribute_type', instance.distribute_type)
        vendor_id = validated_data.get(
            'vendor_id', instance.vendor_id)
        vendor_group_id = validated_data.get(
            'vendor_group_id', instance.vendor_group_id)
        distribution_id = validated_data.get(
            'distribution_id', instance.distribution_id)
        distribute_method = validated_data.get(
            'distribute_method', instance.distribute_method)
        vendor_selection = validated_data.get(
            'vendor_selection', instance.vendor_selection)
        opt_option = validated_data.get(
            'opt_option', instance.opt_option)
        submission_limit = validated_data.get(
            'submission_limit', instance.submission_limit)
        reason = validated_data.get(
            'reason', instance.reason)

        if submission_limit not in [None, instance.submission_limit]:
            program_id = self.context["request"].data['program_id']
            result = get_vendor_submitted_candidates(
                self.context["request"], program_id, job_uid, vendor_id)
            if submission_limit < result["total_records"]:
                submission_limit = result["total_records"]

            if submission_limit_vendor is not None:
                if result["total_records"] > submission_limit_vendor:
                    submission_limit = result["total_records"]

        try:
            obj = VendorJobMapping.objects.get(
                program_id=program_id,
                job_id=job_id,
                vendor_id=vendor_id
            )
            if obj.id != instance.id:
                raise serializers.ValidationError("Duplicate Data")
        except VendorJobMapping.DoesNotExist:
            pass

        instance.program_id = program_id
        instance.job_id = job_id
        instance.distribute_type = distribute_type
        instance.vendor_id = vendor_id
        instance.vendor_group_id = vendor_group_id
        instance.distribution_id = distribution_id
        instance.distribute_method = distribute_method
        instance.vendor_selection = vendor_selection
        instance.opt_option = opt_option
        instance.reason = reason
        instance.modified_by = self.context["user_id"]
        instance.submission_limit = submission_limit

        instance.save()
        return instance

    def get_vendor(self, obj):
        """ get vendor details from the configurator """
        result = collections.OrderedDict({})

        try:
            vendor_info = get_vendor_details(
                self.context["request"],
                settings.VENDOR_ENDPOINT,
                obj.vendor_id,
            )
            if vendor_info is not None:
                result = vendor_info
        except Exception as errors:
            settings.LOGGER.error(
                "VendorJobMappingSerializer >> get_vendor >> error: {}".format(
                    errors))

        return result

    def get_created_by(self, obj):
        user_info = RemoteUserDataHandler.get_user(user_id=obj.created_by)
        if user_info is not None:
            return collections.OrderedDict({
                'id': user_info.id,
                # 'name_prefix': user_info.name_prefix,
                'first_name': user_info.first_name,
                # 'middle_name': user_info.middle_name,
                'last_name': user_info.last_name,
                'email': user_info.email
                # 'name_suffix': user_info.name_suffix
            })
        else:
            return collections.OrderedDict({})

    def get_modified_by(self, obj):
        user_info = RemoteUserDataHandler.get_user(user_id=obj.modified_by)
        if user_info is not None:
            return collections.OrderedDict({
                'id': user_info.id,
                # 'name_prefix': user_info.name_prefix,
                'first_name': user_info.first_name,
                # 'middle_name': user_info.middle_name,
                'last_name': user_info.last_name,
                'email': user_info.email
                # 'name_suffix': user_info.name_suffix
            })
        else:
            return collections.OrderedDict({})

    def get_submissions(self, obj):
        result = get_vendor_submitted_candidates(
            self.context["request"], obj.program_id, obj.job.uid,
            obj.vendor_id)
        return result["total_records"]

    def get_created_on(self, obj):
        return obj.created_on.strftime("%Y-%m-%d %H:%M:%S+00:00")

    def get_modified_on(self, obj):
        return obj.modified_on.strftime("%Y-%m-%d %H:%M:%S+00:00")


class OptInOptOutSerializer(serializers.Serializer):
    opt_option = serializers.ChoiceField(choices=opt_option)
    reason = serializers.ChoiceField(required=False, choices=opt_out_reasons)


class ScheduleJobVendorMappingSerializer(serializers.ModelSerializer):
    uid = serializers.UUIDField(required=False, write_only=True)
    program_id = serializers.UUIDField(required=False, write_only=True)
    job = JobListSerializerV2(many=False, read_only=True)
    job_id = serializers.UUIDField(required=False, write_only=True)
    vendor_id = serializers.UUIDField(required=False, write_only=True)
    vendor = serializers.SerializerMethodField(required=False, read_only=True)
    vendor_group_id = serializers.UUIDField(required=False)
    distribution_id = serializers.CharField(required=False)
    submission_limit = serializers.IntegerField(required=False)
    created_by = serializers.SerializerMethodField()
    modified_by = serializers.SerializerMethodField()
    submissions = serializers.SerializerMethodField(read_only=True)
    created_on = serializers.SerializerMethodField()
    modified_on = serializers.SerializerMethodField()

    class Meta:
        """
        Meta class for Job Serializer
        """
        model = ScheduleJobVendorMapping
        fields = "__all__"

    def create(self, validated_data):

        job_uid = validated_data.get("job_id")

        job_obj = Job.objects.filter(uid=job_uid)

        if not job_obj:
            raise serializers.ValidationError("Valid Job id is reqired")

        job_id = job_obj[0].id
        submission_limit_vendor = job_obj[0].submission_limit_vendor

        submission_limit = validated_data.get("submission_limit", 0)
        scheduled_datetime = validated_data.get("scheduled_datetime", None)

        validated_data.update({"job_id": job_id})

        if submission_limit is not None:
            program_id = self.context["request"].data['program_id']
            job_uid = job_obj[0].uid
            vendor_id = validated_data.get("vendor_id")
            result = get_vendor_submitted_candidates(
                self.context["request"], program_id, job_uid, vendor_id)

            if submission_limit < result["total_records"]:
                submission_limit = result["total_records"]

            if submission_limit_vendor is not None:
                if result["total_records"] > submission_limit_vendor:
                    submission_limit = result["total_records"]

        vendor_job_obj, is_created = ScheduleJobVendorMapping.objects.get_or_create(
            program_id=program_id,
            job_id=job_id,
            vendor_id=validated_data.get("vendor_id")
        )

        if is_created:
            vendor_job_obj.distribute_type = validated_data.get(
                "distribute_type")
            vendor_job_obj.vendor_group_id = validated_data.get(
                "vendor_group_id")
            vendor_job_obj.distribution_id = validated_data.get(
                "distribution_id")
            vendor_job_obj.scheduled_datetime = scheduled_datetime
            vendor_job_obj.submission_limit = submission_limit
            user_id = self.context["user_id"]
            vendor_job_obj.created_by = user_id
            vendor_job_obj.modified_by = user_id
            vendor_job_obj.save()

        return vendor_job_obj

    def update(self, instance, validated_data):
        """
        update the instance
        :param instance:
        :type instance:
        :param validated_data:
        :type validated_data:
        :return:
        :rtype:
        """
        program_id = validated_data.get(
            'program_id', instance.program_id)

        job_uid = validated_data.get("job_id")

        if job_uid:
            job_obj = Job.objects.filter(uid=job_uid)

            if not job_obj:
                raise serializers.ValidationError("Valid Job id is reqired")

            job_id = job_obj[0].id
            submission_limit_vendor = job_obj[0].submission_limit_vendor
        else:
            job_id = instance.job_id
            job_uid = instance.job.uid
            submission_limit_vendor = instance.job.submission_limit_vendor

        distribute_type = validated_data.get(
            'distribute_type', instance.distribute_type)
        vendor_id = validated_data.get(
            'vendor_id', instance.vendor_id)
        vendor_group_id = validated_data.get(
            'vendor_group_id', instance.vendor_group_id)
        distribution_id = validated_data.get(
            'distribution_id', instance.distribution_id)
        scheduled_status = validated_data.get(
            'scheduled_status', instance.scheduled_status)
        submission_limit = validated_data.get(
            'submission_limit', instance.submission_limit)

        if submission_limit not in [None, instance.submission_limit]:
            program_id = self.context["request"].data['program_id']
            result = get_vendor_submitted_candidates(
                self.context["request"], program_id, job_uid, vendor_id)
            if submission_limit < result["total_records"]:
                submission_limit = result["total_records"]

            if submission_limit_vendor is not None:
                if result["total_records"] > submission_limit_vendor:
                    submission_limit = result["total_records"]

        try:
            obj = ScheduleJobVendorMapping.objects.get(
                program_id=program_id,
                job_id=job_id,
                vendor_id=vendor_id
            )
            if obj.id != instance.id:
                raise serializers.ValidationError("Duplicate Data")
        except ScheduleJobVendorMapping.DoesNotExist:
            pass

        instance.program_id = program_id
        instance.job_id = job_id
        instance.distribute_type = distribute_type
        instance.vendor_id = vendor_id
        instance.vendor_group_id = vendor_group_id
        instance.distribution_id = distribution_id
        instance.scheduled_status = scheduled_status
        instance.submission_limit = submission_limit
        instance.modified_by = self.context["user_id"]

        instance.save()
        return instance

    def get_vendor(self, obj):
        """ get vendor details from the configurator """
        result = collections.OrderedDict({})

        try:
            vendor_info = get_vendor_details(
                self.context["request"],
                settings.VENDOR_ENDPOINT,
                obj.vendor_id,
            )
            if vendor_info is not None:
                result = vendor_info
        except Exception as errors:
            settings.LOGGER.error(
                "VendorJobMappingSerializer >> get_vendor >> error: {}".format(
                    errors))

        return result

    def get_created_by(self, obj):
        user_info = RemoteUserDataHandler.get_user(user_id=obj.created_by)
        if user_info is not None:
            return collections.OrderedDict({
                'id': user_info.id,
                # 'name_prefix': user_info.name_prefix,
                'first_name': user_info.first_name,
                # 'middle_name': user_info.middle_name,
                'last_name': user_info.last_name,
                'email': user_info.email
                # 'name_suffix': user_info.name_suffix
            })
        else:
            return collections.OrderedDict({})

    def get_modified_by(self, obj):
        user_info = RemoteUserDataHandler.get_user(user_id=obj.modified_by)
        if user_info is not None:
            return collections.OrderedDict({
                'id': user_info.id,
                # 'name_prefix': user_info.name_prefix,
                'first_name': user_info.first_name,
                # 'middle_name': user_info.middle_name,
                'last_name': user_info.last_name,
                'email': user_info.email
                # 'name_suffix': user_info.name_suffix
            })
        else:
            return collections.OrderedDict({})

    def get_submissions(self, obj):
        result = get_vendor_submitted_candidates(
            self.context["request"], obj.program_id, obj.job.uid,
            obj.vendor_id)
        return result["total_records"]

    def get_created_on(self, obj):
        return obj.created_on.strftime("%Y-%m-%d %H:%M:%S+00:00")

    def get_modified_on(self, obj):
        return obj.modified_on.strftime("%Y-%m-%d %H:%M:%S+00:00")

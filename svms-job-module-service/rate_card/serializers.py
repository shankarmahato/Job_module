from django.conf import settings
from rest_framework import serializers

from job.models import Job, FoundationData
from job_catalog.models import JobCategory, JobTitle
from .models import RateCard, RateCardConfig, rate_rule, RatesOfRateCard


class RateCardJobCategorySerializer(serializers.ModelSerializer):
    """
    serializer for Job Category
    """

    class Meta:
        """
        Meta class for Job Category
        """
        model = JobCategory
        fields = (
            'id',
            'o_net_soc_code',
            'category_name',
        )
        read_only_fields = (
            'id',
            'o_net_soc_code',
            'category_name',
        )


class RateCardJobTitleSerializer(serializers.ModelSerializer):
    """
    serializer for Rate Card Job Title
    """

    class Meta:
        """
        Meta class for Rate Card Job Title
        """
        model = JobTitle
        fields = (
            'id',
            'title',
            'level',
        )
        read_only_fields = (
            'id',
            'title',
            'level'
        )


class RateCardJobTemplateSerializer(serializers.ModelSerializer):
    """
    serializer for Rate Card Job Template Serializer
    """

    class Meta:
        """
        Meta class for Rate Card Job Template
        """
        model = Job
        fields = (
            'id',
            'title',
        )
        read_only_fields = (
            'id',
            'title',
        )


class RateCardFoundationalDataSerializer(serializers.ModelSerializer):
    """
    serializer for Rate Card Foundational Data Serializer
    """

    class Meta:
        """
        Meta class for Rate Card Foundational Data Serializer
        """
        model = FoundationData
        fields = (
            'id',
            'cost_center',
            'company_code',
            'gl_code',
            'source_code',
            'market_region',
            'work_location'
        )
        read_only_fields = fields


class RatesOfRateCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatesOfRateCard
        fields = "__all__"


class RatesOfRateCardSerializerV2(serializers.Serializer):
    unit_of_measure = serializers.CharField()
    min_rate = serializers.FloatField(default=0.0)
    max_rate = serializers.FloatField(default=0.0)
    min_rate_rule = serializers.ChoiceField(required=False, choices=rate_rule,
                                            default="Can Change")
    max_rate_rule = serializers.ChoiceField(required=False,
                                            choices=rate_rule,
                                            default="Can Change")
    is_active = serializers.BooleanField(default=True)


class RateCardSerializer(serializers.ModelSerializer):
    """This serializer is used to serialize RateCard data."""

    program_id = serializers.CharField(required=False)
    job_category = RateCardJobCategorySerializer(many=False, read_only=True)
    job_category_id = serializers.IntegerField(write_only=True)
    job_title = RateCardJobTitleSerializer(many=False, read_only=True)
    job_title_id = serializers.IntegerField(write_only=True)
    job_template = RateCardJobTemplateSerializer(many=False, read_only=True)
    job_template_id = serializers.IntegerField(write_only=True, required=False)
    # foundational_data_type = RateCardFoundationalDataSerializer(
    #     many=False, read_only=True)
    # foundational_data_type_id = serializers.IntegerField(
    #     write_only=True, required=False)
    work_location = serializers.CharField(required=False)
    hierarchy = serializers.CharField(required=False)
    region = serializers.CharField(required=False)
    rates_of_rate_card = RatesOfRateCardSerializer(many=True, read_only=True)
    rates = RatesOfRateCardSerializerV2(many=True, write_only=True,
                                        required=False)
    active_jobs = serializers.SerializerMethodField(required=False,
                                                    read_only=True)
    active_rates = serializers.SerializerMethodField(required=False,
                                                     read_only=True)

    class Meta:
        model = RateCard
        fields = "__all__"

    def create(self, validated_data):
        """
        handling the unique together
        :param validated_data:
        :type validated_data:
        :return:
        :rtype:
        """
        if validated_data.get("hierarchy") and not validated_data.get(
                "work_location"):
            raise serializers.ValidationError(
                "work_location is mandatory when  hierarchy is associated ")

        rate_obj = RateCard.objects.filter(
            program_id=validated_data.get("program_id"),
            job_category_id=validated_data.get("job_category_id"),
            job_title_id=validated_data.get("job_title_id"),
            job_level=validated_data.get("job_level"),
            job_template_id=validated_data.get("job_template_id"),
            hierarchy=validated_data.get("hierarchy"),
            work_location=validated_data.get("work_location"),
            region=validated_data.get("region"),
            currency=validated_data.get("currency"),
        )
        if rate_obj:
            raise serializers.ValidationError("data already exists")

        rate_list = validated_data.pop("rates", [])

        if not rate_list:
            raise serializers.ValidationError(
                "rates under rate card is missing")

        rate_card_obj = RateCard.objects.create(**validated_data)
        for rate in rate_list:
            RatesOfRateCard.objects.create(
                rate_card_id=rate_card_obj.pk,
                unit_of_measure=rate["unit_of_measure"],
                min_rate=rate["min_rate"],
                max_rate=rate["max_rate"],
                min_rate_rule=rate["min_rate_rule"],
                max_rate_rule=rate["max_rate_rule"],
                is_active=rate["is_active"])

        return rate_card_obj

    def update(self, instance, validated_data):
        """
        update rate card
        :param instance:
        :type instance:
        :param validated_data:
        :type validated_data:
        :return:
        :rtype:
        """

        try:
            hierarchy = validated_data.get(
                "hierarchy", instance.hierarchy)
            work_location = validated_data.get(
                "work_location", instance.work_location)

            if hierarchy and not work_location:
                raise serializers.ValidationError(
                    "work_location is mandatory when  hierarchy is associated ")

            rate_obj = RateCard.objects.get(
                program_id=validated_data.get(
                    "program_id", instance.program_id),
                job_category_id=validated_data.get(
                    "job_category_id", instance.job_category_id),
                job_title_id=validated_data.get(
                    "job_title_id", instance.job_title_id),
                job_level=validated_data.get("job_level", instance.job_level),
                job_template_id=validated_data.get(
                    "job_template_id", instance.job_template_id),
                hierarchy=validated_data.get("hierarchy", instance.hierarchy),
                work_location=validated_data.get(
                    "work_location", instance.work_location),
                region=validated_data.get("region", instance.region),
                currency=validated_data.get("currency", instance.currency)
            )
            if instance.pk != rate_obj.pk:
                raise serializers.ValidationError(
                    """ unique combination for (program_id, job_category_id, 
                    job_title_id, job_level, job_template_id, hierarchy,
                    foundational_data_type_id, region and currency) 
                    already exists for same program_id
                    """)

        except RateCard.DoesNotExist:
            pass

        instance.program_id = validated_data.get(
            "program_id", instance.program_id)
        instance.job_category_id = validated_data.get(
            "job_category_id", instance.job_category_id)
        instance.job_title_id = validated_data.get(
            "job_title_id", instance.job_title_id)
        instance.job_level = validated_data.get(
            "job_level", instance.job_level)
        instance.job_template_id = validated_data.get(
            "job_template_id", instance.job_template_id)
        instance.hierarchy = hierarchy
        instance.work_location = work_location
        instance.region = validated_data.get("region", instance.region)
        instance.currency = validated_data.get("currency", instance.currency)

        rate_list = validated_data.pop("rates", [])

        for rate in rate_list:
            rate_obj, is_created = RatesOfRateCard.objects.get_or_create(
                rate_card_id=instance.pk,
                unit_of_measure=rate["unit_of_measure"],
            )
            rate_obj.min_rate = rate["min_rate"]
            rate_obj.max_rate = rate["max_rate"]
            rate_obj.min_rate_rule = rate["min_rate_rule"]
            rate_obj.max_rate_rule = rate["max_rate_rule"]
            rate_obj.is_active = rate["is_active"]
            rate_obj.save()

        instance.save()
        return instance

    def get_active_jobs(self, obj):
        """
            Show the no.of active jobs which are associated with the selected rate
            card configuration that means count of active jobs for which rate card
            was picked up and inherited the rates into job while  creating/editing
            the job.
            Show the count of all jobs not in closed status those are matched with
            the Job category, Job title and Currency of the Rate card.

            @param obj:
            @type obj:
            @return:
            @rtype:
        """

        count_val = 0

        try:
            count_val = Job.objects.select_related().filter(
                is_enabled=True,
                category_id=obj.job_category.id,
                title_id=obj.job_title.id,
                currency=obj.currency).count()
        except Exception as error:
            settings.LOGGER.info(
                "RateCardSerializer >> get_active_jobs >> rate card pk : {}, error: {}".format(
                    obj.id, error))

        return count_val

    def get_active_rates(self, obj):
        """
            Show the list of active rates defined under the respective rate card
            In case there are no rates existed except the default rate
            (which should be created as soon as Rate card is created) for the rate
            card, show Active rates count to the extent of respective UOMs selected
            in the respective rate card. E.g, If user selected Hourly and Daily
            UOMs and defined the default rates, then Active rate count would be 2
            unless user explicitly created rates under the respective rate card.

            @param obj:
            @type obj:
            @return:
            @rtype:
        """

        return obj.rates_of_rate_card.filter(is_active=True).count()


class RateCardConfigSerializer(serializers.ModelSerializer):
    """
    Rate Card Config Serializer
    """
    program_id = serializers.UUIDField(required=False)
    config_json = serializers.JSONField(required=False, default=dict)

    class Meta:
        model = RateCardConfig
        fields = "__all__"

    def create(self, validated_data):
        """

        @param validated_data:
        @type validated_data:
        @return:
        @rtype:
        """

        rate_card_config_obj = RateCardConfig.objects.create(**validated_data)

        return rate_card_config_obj

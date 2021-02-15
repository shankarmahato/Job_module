from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.pagination import LimitOffsetPagination
from connectors.vms_profile_manager.serializers import RemoteUserInfoSerializer

from job_catalog.models import (
    JobCatalog, JobCategory, JobTag, JobTitle, Industry
)


class IndustrySerializer(serializers.ModelSerializer):
    """This serializer is used to serialize industry data."""

    class Meta:
        model = Industry
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    """
    serializer for  to Category
    """

    class Meta:
        model = JobCategory
        fields = '__all__'

class CategoryListSerializer(serializers.ModelSerializer):
    """
    serializer for  to Category
    """

    class Meta:
        model = JobCategory
        fields = ('id','o_net_soc_code','category_name','description')


class JobTagSerializer(serializers.ModelSerializer):
    """
    serializer for  to Job Tag
    """

    class Meta:
        model = JobTag
        fields = (
            'id',
            'tag',
        )


class EditedBySerializer(serializers.ModelSerializer):
    """
    serializer for edited By user
    """

    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )


class JobTitleSerializer(serializers.ModelSerializer):
    """
    serializer for Job Title
    """

    job_tag = JobTagSerializer(many=True, required=True)

    # last_edited_by = EditedBySerializer()

    class Meta:
        """
        Meta class for Job Title
        """
        model = JobTitle
        fields = ('id',
                  'uid',
                  'program_id',
                  'category',
                  'title',
                  'level',
                  'description',
                  'status',
                  'job_tag',
                  'created_by',
                  'created_on',
                  'modified_by',
                  'modified_on'
                  )
        read_only_fields = (
            'id',
            'uid',
        )

    def create(self, validated_data):

        job_tags = validated_data.pop('job_tag')
        job_title = JobTitle.objects.create(**validated_data)

        tag_objs = []
        for tag in job_tags:
            if tag:
                job_tag, _ = JobTag.objects.get_or_create(tag=tag["tag"])
                tag_objs.append(job_tag)

        if tag_objs:
            job_title.job_tag.add(*tag_objs)
            job_title.save()

        return job_title

    def update(self, instance, validated_data):
        # instance.categorie_id = validated_data.get(
        #     'program_id', instance.program_id)
        # instance.categorie_id = validated_data.get(
        #     'categorie_id', instance.categorie_id)
        # instance.title = validated_data.get('title', instance.title)
        instance.level = validated_data.get(
            'level', instance.level)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        # instance.created_by = validated_data.get(
        #     'created_by', instance.created_by)
        instance.modified_by = validated_data.get(
            'modified_by', instance.modified_by)
        job_tags = validated_data.get('job_tag')
        tag_objs = []
        for tag in job_tags:
            if tag:
                job_tag, _ = JobTag.objects.get_or_create(tag=tag["tag"])
                tag_objs.append(job_tag)

        instance.job_tag.clear()
        if tag_objs:
            instance.job_tag.add(*tag_objs)

        instance.save()
        return instance


class JobTitleReadSerializer(RemoteUserInfoSerializer):
    """
    serializer for Job Title
    """
    category = serializers.CharField(source='category.o_net_soc_code')
    job_tag = JobTagSerializer(many=True, required=True)

    # last_edited_by = EditedBySerializer()

    class Meta:
        """
        Meta class for Job Title
        """
        model = JobTitle
        fields = ('id',
                  'uid',
                  'program_id',
                  'category',
                  'title',
                  'level',
                  'description',
                  'status',
                  'job_tag',
                  'created_by',
                  'created_on',
                  'modified_by',
                  'modified_on'
                  )
        read_only_fields = (
            'id',
            'uid',
        )


class JobCategorySerializer(serializers.ModelSerializer):
    """
    serializer for Job Category
    """
    # job_title = JobTitleSerializer(many=True, read_only=True)

    job_title = serializers.SerializerMethodField('get_job_titles')

    def get_job_titles(self, *args):
        """
        get job titles based on the given program id
        :param args:
        :type args:
        :return:
        :rtype:
        """
        program_id = self.context.get("program_id")
        request_obj = self.context.get("request_obj")
        if program_id:
            qs = JobTitle.objects.filter(program_id=program_id)
        else:
            qs = JobTitle.objects.all()

        if request_obj:
            paginator = LimitOffsetPagination()
            paginator.limit_query_param = "job_title_limit"
            paginator.offset_query_param = "job_title_offset"
            qs = paginator.paginate_queryset(qs, request_obj)
        serializer = JobTitleSerializer(qs, many=True)
        return serializer.data

    class Meta:
        """
        Meta class for Job Category
        """
        model = JobCategory
        fields = (
            'o_net_soc_code',
            'category_name',
            'description',
            'job_title'
        )
        read_only_fields = (
            'o_net_soc_code',
            'category_name',
        )


class JobCatalogSerializer(serializers.ModelSerializer):
    """
    serializer for Job Catalog
    """
    category = JobCategorySerializer()

    class Meta:
        """
        Meta class for Job Catalog
        """
        model = JobCatalog
        fields = '__all__'
        # read_only_fields = ('category__title', 'category__category_name')


class JobTitleListSerializer(serializers.ModelSerializer):
    """
    serializer for Job Title
    """

    job_tag = JobTagSerializer(many=True, required=True)

    # last_edited_by = EditedBySerializer()

    class Meta:
        """
        Meta class for Job Title
        """
        model = JobTitle
        fields = ('id',
                  
                  'title',
                  'level',
                  'description',
                  'job_tag',
                  )

class JobCategoryTitleSerializer(serializers.ModelSerializer):
    """
    serializer for Job Title
    """

    class Meta:
        """
        Meta class for Job Title
        """
        model = JobTitle
        fields = (
                'id',
                  'uid',
                  'category',
                  'title',
                  )

        depth = 1
from django.contrib import admin
from job.models import JobConfiguration,Job,JobCustom,FoundationData,FoundationQualificationData
from rangefilter.filter import DateRangeFilter


class FoundationQualificationDataAdmin(admin.ModelAdmin):

    def qs_fd_id(self, obj):
        return obj.entity_id

    def qs_fd_type(self, obj):
        return obj.entity_type

    def qs_fd_key(self, obj):
        return obj.entity_key

    def qs_fd_name(self, obj):
        return obj.entity_name

    def qs_fd_value(self, obj):
        return obj.entity_value

    qs_fd_id.short_description = 'Qualification/FD_id'
    qs_fd_type.short_description = 'Qualification/FD_type'
    qs_fd_name.short_description = 'is_Qualification_or_FD'
    qs_fd_key.short_description = 'Qualification/FD_type_id'
    qs_fd_value.short_description = 'Qualification/FD_level'

    list_display = (
        "uid",
        "program_id",
        "job",
        "qs_fd_id",
        "qs_fd_type",
        "qs_fd_name",
        "qs_fd_key",
        "qs_fd_value",
        "entity_is_active"
    )

    list_filter = (
        "program_id",
        "entity_is_active"
    )

    search_fields = (
        "uid",
        "program_id",
        "job__uid",
        "qs_fd_id",
        "qs_fd_type",
        "qs_fd_name",
        "qs_fd_key",
        "qs_fd_value",
        "entity_is_active"
    )

    raw_id_fields = ("job",)


class JobAdmin(admin.ModelAdmin):

    def get_readonly_fields(self, request, obj=None):

        if obj and obj.is_template == True:
            return self.readonly_fields + ('template','job_id','source_id','source')

        return self.readonly_fields


    list_display = (
        "id",
        "uid",
        "program_id",
        "category",
        "title",
        "is_enabled",
        "is_delete",
        "created_by",
        "created_on"
    )

    list_filter = (
        ("created_on", DateRangeFilter),
        "program_id",
        "schedule_interview",
        "status",
        "submit_type",
        "is_template"
    )

    search_fields = (
        "uid",
        "program_id",
        "job_manager",
        "msp_manager",
        "created_by",
        "template_name"
    )

    raw_id_fields = ("category", "title")


class JobCustomAdmin(admin.ModelAdmin):

    list_display = (
        "uid",
        "program_id",
        "job",
        "is_delete",
        "created_by",
        "created_on"
    )

    list_filter = (
        ("created_on", DateRangeFilter),
        "program_id",
    )

    search_fields = (
        "uid",
        "program_id",
        "job__uid"
    )

# Register your models here.


admin.site.register(FoundationQualificationData, FoundationQualificationDataAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(JobCustom, JobCustomAdmin)

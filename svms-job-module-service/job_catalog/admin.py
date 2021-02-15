from django.contrib import admin
from django_filters import Filter

from .models import Industry, JobCategory, JobCatalog, JobTitle, JobTag


class IndustryAdmin(admin.ModelAdmin):
    """
    Industry Model Admin

    """
    list_display = ('id','uid', 'naics_code', 'industry_type')
    list_filter = ('naics_code',)
    search_fields = ('naics_code', 'id')


class JobTitleAdmin(admin.ModelAdmin):
    """
    Job Title Model Admin
    """
    list_display = ('id', 'uid', 'program_id', 'title', 'category', 'status')
    list_filter = ('program_id', 'category', 'status')
    search_fields = ('id', 'category', 'title')
    raw_id_fields = ('category', 'job_tag')


class JobCategoryAdmin(admin.ModelAdmin):
    """
    Job Category Model Admin
    """
    list_display = ('id','uid', 'o_net_soc_code', 'category_name')
    list_filter = ('o_net_soc_code',)
    search_fields = ('id', 'o_net_soc_code')


class JobCatalogAdmin(admin.ModelAdmin):
    """
    Job Catalog Model Admin
    """
    list_display = ('id', 'uid','naics_code', 'category')
    list_filter = ('naics_code', 'category',)
    search_fields = ('id', 'naics_code')
    raw_id_fields = ('naics_code', 'category')


class JobTagAdmin(admin.ModelAdmin):
    """
        Job Catalog Model Admin
        """
    list_display = ('id', 'tag',)
    list_filter = ('tag',)
    search_fields = ('id', 'tag')


# Register your models here

admin.site.register(Industry, IndustryAdmin)
admin.site.register(JobCategory, JobCategoryAdmin)
admin.site.register(JobTitle, JobTitleAdmin)
admin.site.register(JobCatalog, JobCatalogAdmin)
admin.site.register(JobTag, JobTagAdmin)
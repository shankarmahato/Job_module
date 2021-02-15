from django.contrib import admin

from .models import RateCard, RateCardConfig, RatesOfRateCard


class RateCardConfigAdmin(admin.ModelAdmin):
    search_fields = ('program_id',)
    list_display = search_fields


class RatesOfRateCardAdmin(admin.ModelAdmin):
    search_fields = (
        'rate_card', "unit_of_measure", "min_rate", "max_rate", "min_rate_rule",
        "max_rate_rule", "is_active")
    list_display = search_fields


class RateCardAdmin(admin.ModelAdmin):
    """
    RateCard Model Admin

    """
    search_fields = (
        'program_id', 'job_category__category_name', 'job_title__title',
        'job_level', 'job_template__id',
        'hierarchy', 'work_location',
        'region', 'currency')
    list_display = ('program_id', 'job_category',
                    'job_title', 'job_level',
                    'job_template', 'hierarchy',
                    'work_location', 'region', 'currency',
                    )


admin.site.register(RateCardConfig, RateCardConfigAdmin)
admin.site.register(RateCard, RateCardAdmin)
admin.site.register(RatesOfRateCard, RatesOfRateCardAdmin)

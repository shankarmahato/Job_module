from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import VendorJobMapping, ScheduleJobVendorMapping

admin.site.register(VendorJobMapping)

admin.site.register(ScheduleJobVendorMapping)

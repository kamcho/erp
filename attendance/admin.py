from django.contrib import admin
from .models import Device, LateTimeRule

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'school', 'last_sync')
    search_fields = ('name', 'school__name')
    list_filter = ('school',)

@admin.register(LateTimeRule)
class LateTimeRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'late_time')
    filter_horizontal = ('grades',)
    list_filter = ('school',)
    search_fields = ('name',)


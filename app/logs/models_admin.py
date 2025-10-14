from django.contrib import admin
from common.exportCSV import export_to_csv
from rangefilter.filters import (
    DateRangeFilterBuilder,  
)

class LogsAdmin(admin.ModelAdmin):
    list_display = ('typed', 'msg', 'path', 'created_at')
    list_filter = ('typed', ('created_at', DateRangeFilterBuilder()))
    search_fields = ('msg',)
    
    actions = [export_to_csv]

class LogEndpointAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'method', 'student', 'status_code', 'timestamp')
    search_fields = ('endpoint', 'student__name')
    list_filter = ('method', 'status_code', ('timestamp', DateRangeFilterBuilder()))

class LogsAnamneseErrorAdmin(admin.ModelAdmin):
    list_display = ('student', 'created_at', 'url_anamnese')
    search_fields = ('student__name', 'url_anamnese')
    list_filter = ('created_at', ('created_at', DateRangeFilterBuilder()))
    actions = [export_to_csv]

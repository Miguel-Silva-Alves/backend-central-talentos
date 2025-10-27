from django.contrib import admin

from rh.models import File
from common.exportCSV import export_to_csv
# Register your models here.
class FileAdmin(admin.ModelAdmin):  
    actions=[export_to_csv]

admin.site.register(File, FileAdmin)

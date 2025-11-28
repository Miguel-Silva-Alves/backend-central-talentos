from django.contrib import admin

from rh.models import File, Certificate, Curriculum, History, Formation
from common.exportCSV import export_to_csv
# Register your models here.
class FileAdmin(admin.ModelAdmin):  
    actions=[export_to_csv]
    list_display = ['pk', 'name', 'date_upload']

admin.site.register(File, FileAdmin)
admin.site.register(Certificate)
admin.site.register(Curriculum)
admin.site.register(History)
admin.site.register(Formation)

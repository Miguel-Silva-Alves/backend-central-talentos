from django.contrib import admin

# Register your models here.
from ai.models import Queries, Indication

admin.site.register(Queries)
admin.site.register(Indication)
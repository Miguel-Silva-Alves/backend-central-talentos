from django.contrib import admin

# Models
from company.models import Company, Candidate, Profile

# Register your models here.
admin.site.register(Company)
admin.site.register(Candidate)
admin.site.register(Profile)
from django.contrib import admin
from .models.companyModel import Company
from .models.companyScoreModel import CompanyScore

# Register your models here.
admin.site.register(Company)
admin.site.register(CompanyScore)
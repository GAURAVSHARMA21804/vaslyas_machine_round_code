from .models.companyModel import Company
from django.db import transaction

object = [Company(name=f"Company{i}",industry=f"Industry{i}",state=f"State{i}",annual_revenue=1000000,employee_count=100,compliance_score=90) for i in range(100000)]

chunk_size = 10000
with transaction.atomic():
    for i in range(0, len(object), chunk_size):
        Company.objects.bulk_create(object[i:i+chunk_size])
from django.core.management.base import BaseCommand
from serviceApp.models.companyModel import Company
from serviceApp.models.companyScoreModel import CompanyScore
from datetime import timedelta, datetime
from django.db import transaction
from django.db.models import Window, F
from django.db.models.functions import DenseRank
from serviceApp.utils import calculate_company_score

# def now():
#     return datetime.now(timezone.utc)

class Command(BaseCommand):
    help = 'Create companies record in database'

    def handle(self, *args, **options):
        object = [Company(name=f"Company{i}",industry=f"Industry{i}",state=f"State{i}",annual_revenue=1000000,employee_count=100,compliance_score=90) for i in range(100000)]

        chunk_size = 10000
        with transaction.atomic():
            for i in range(0, len(object), chunk_size):
                Company.objects.bulk_create(object[i:i+chunk_size])
                
        self.stdout.write(self.style.SUCCESS('Companies record created successfully'))

        self.insert_company_score() 
        self.insert_company_score_rank()

    def insert_company_score(self):
        companies = Company.objects.all()
        for company in companies:
            total_score = calculate_company_score(company) 
            CompanyScore.objects.create(company=company, total_score=total_score, calculated_at=datetime.now())
        self.stdout.write(self.style.SUCCESS('Company scores created successfully'))

    def insert_company_score_rank(self):
        annotated_scores = CompanyScore.objects.annotate(
            dense_rank=Window(
                expression=DenseRank(),
                order_by=[F("total_score").desc()],
            )
        )

        to_update = [
            CompanyScore(id=obj.id, rank=obj.dense_rank)
            for obj in annotated_scores
        ]

        if to_update:
            CompanyScore.objects.bulk_update(to_update, ["rank"])

        self.stdout.write(self.style.SUCCESS('Company scores ranks created successfully'))


from django.db.models import Q
from .models.companyModel import Company
from .models.companyScoreModel import CompanyScore
from django.utils import timezone
now = timezone.now()

def calculate_company_score(company):
    compliance_score = company.compliance_score
    revenue_score = min(company.annual_revenue/1000000,100)
    total_score = (revenue_score*0.6 + compliance_score*0.4)
    return total_score
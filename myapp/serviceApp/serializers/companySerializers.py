from rest_framework import serializers
from ..models.companyModel import Company
from ..models.companyScoreModel import CompanyScore

class CompanyListSerializer(serializers.ModelSerializer):
    total_score = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField() 
    class Meta:
        model = Company
        fields = ['id', 'name', 'industry', 'state', 'annual_revenue', 'total_score', 'rank']
        read_only_fields = ['id', 'create_at', 'total_score', 'rank']


    def get_total_score(self, obj):
        try:
            company_score = CompanyScore.objects.get(company=obj)
            return company_score.total_score
        except CompanyScore.DoesNotExist:
            return None

    def get_rank(self, obj):
        try:
            company_score = CompanyScore.objects.get(company=obj)
            return company_score.rank
        except CompanyScore.DoesNotExist:
            return None

class CompanyDetailSerializer(serializers.ModelSerializer):
    total_score = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField() 
    calculated_at = serializers.SerializerMethodField()
    class Meta:
        model = Company
        fields = ['id','name', 'industry', 'state', 'annual_revenue', 'employee_count', 'total_score', 'rank', 'calculated_at']

        read_only_fields = ['id']

    def get_total_score(self, obj):
        try:
            company_score = CompanyScore.objects.get(company=obj)
            return company_score.total_score
        except CompanyScore.DoesNotExist:
            return None

    def get_rank(self, obj):
        try:
            company_score = CompanyScore.objects.get(company=obj)
            return company_score.rank
        except CompanyScore.DoesNotExist:
            return None

    def get_calculated_at(self, obj):
        try:
            company_score = CompanyScore.objects.get(company=obj)
            return company_score.calculated_at
        except CompanyScore.DoesNotExist:
            return None
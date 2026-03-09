from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Company(models.Model):
    name = models.CharField(max_length=50)
    industry = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    annual_revenue = models.IntegerField()
    employee_count=models.IntegerField()
    compliance_score = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)])
    is_active = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        indexes = [

            models.Index(fields=['industry'],name='industry_idx'),
            models.Index(fields=['annual_revenue'],name='annual_revenue_idx'),
            models.Index(fields=['is_active'],name='is_active_idx')

        ]
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from .companyModel import Company

class CompanyScore(models.Model):
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    total_score = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)])
    rank = models.IntegerField(blank=True,null=True)
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company}"

    class Meta:
        indexes = [

            models.Index(fields=['total_score'],name='total_score_idx'),
            models.Index(fields=['rank'],name='rank_idx')

        ]
        
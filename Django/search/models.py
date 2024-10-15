from django.db import models

class DentalClaim(models.Model):
    incomplete_disease_code = models.CharField(max_length=50)  # 불완전 상병 코드
    incomplete_disease_name = models.CharField(max_length=100)  # 불완전 상병명
    claim_category = models.CharField(max_length=100, null=True, blank=True)  # 청구 카테고리 (null 허용)
    claim_detail = models.CharField(max_length=100, null=True, blank=True)  # 세부 청구 항목 (null 허용)

    def __str__(self):
        return self.incomplete_disease_name
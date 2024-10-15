from django.db import models


# 상병코드 (대분류, 중분류, 하위분류 통합)
class DiseaseCode(models.Model):
    code = models.CharField(max_length=20)  # 상병 코드
    name = models.CharField(max_length=255)  # 상병명
    level = models.CharField(max_length=10)  # 레벨: 대분류, 중분류, 하위분류
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )

    def __str__(self):
        return f"{self.code} - {self.name}"  # 코드와 이름 반환


# 보험 대분류
class InsuranceCategory(models.Model):
    name = models.CharField(max_length=255)  # 보험 대분류명

    def __str__(self):
        return self.name


# 보험 중분류
class InsuranceSubCategory(models.Model):
    category = models.ForeignKey(
        InsuranceCategory, on_delete=models.CASCADE
    )  # 보험 대분류와 연결
    name = models.CharField(max_length=255)  # 보험 중분류명
    url = models.URLField(null=True, blank=True)  # URL (참조 링크)

    # 중분류 상병코드와 일대다 연결
    disease_codes = models.ManyToManyField(
        DiseaseCode, related_name="insurance_sub_categories", blank=True
    )

    def __str__(self):
        return self.name  # 보험 중분류명 반환

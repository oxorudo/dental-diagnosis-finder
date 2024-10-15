from django.db import models


# 상병코드 대분류
class DiseaseCategory(models.Model):
    incomplete_code = models.CharField(max_length=20)  # 불완전 상병 코드 (대분류)
    incomplete_name = models.CharField(max_length=255)  # 불완전 상병명 (대분류명)

    def __str__(self):
        return self.incomplete_code  # 코드만 반환


# 상병코드 중분류
class DiseaseSubCategory(models.Model):
    category = models.ForeignKey(
        DiseaseCategory, on_delete=models.CASCADE
    )  # 대분류와 연결
    sub_code = models.CharField(max_length=20, null=True, blank=True)  # 중분류 코드
    name = models.CharField(max_length=255)  # 중분류 상병명

    def __str__(self):
        return f"{self.sub_code} - {self.name}"  # 코드와 이름 반환


# 상병코드 하위분류 (세부 상병 코드)
class DiseaseDetailCode(models.Model):
    sub_category = models.ForeignKey(
        DiseaseSubCategory, on_delete=models.CASCADE
    )  # 중분류와 연결
    detail_code = models.CharField(
        max_length=20, null=True, blank=True
    )  # 하위분류 코드
    detail_name = models.CharField(max_length=255)  # 하위분류 상병명

    def __str__(self):
        return f"{self.detail_code} - {self.detail_name}"  # 코드와 상세명 반환


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

    # 중분류 상병코드와 다대다 연결
    disease_sub_categories = models.ManyToManyField(
        DiseaseSubCategory, related_name="insurance_sub_categories", blank=True
    )

    # 하위분류 상병코드와 다대다 연결
    disease_codes = models.ManyToManyField(
        DiseaseDetailCode, related_name="insurance_sub_categories", blank=True
    )

    def __str__(self):
        return self.name  # 보험 중분류명 반환

from django.contrib import admin
from .models import (
    InsuranceCategory,
    InsuranceSubCategory,
    DiseaseDetailCode,
    DiseaseCategory,
    DiseaseSubCategory,
)


# InsuranceSubCategory에 중분류와 하위분류 상병코드를 함께 선택할 수 있도록 admin 커스터마이징
class InsuranceSubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "url")  # 관리자 페이지에서 보여줄 필드들
    filter_horizontal = (
        "disease_sub_categories",
        "disease_codes",
    )  # ManyToMany 필드를 가로로 필터링


# 모델을 관리자 페이지에 등록
admin.site.register(InsuranceCategory)
admin.site.register(
    InsuranceSubCategory, InsuranceSubCategoryAdmin
)  # 커스터마이징한 admin 등록
admin.site.register(DiseaseCategory)
admin.site.register(DiseaseSubCategory)
admin.site.register(DiseaseDetailCode)

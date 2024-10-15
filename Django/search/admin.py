from django.contrib import admin
from .models import (
    InsuranceCategory,
    InsuranceSubCategory,
    DiseaseCode,
)


class DiseaseCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "level",
        "parent",
    )  # 관리자 페이지에서 보여줄 필드들


# 모델을 관리자 페이지에 등록
admin.site.register(InsuranceCategory)
admin.site.register(InsuranceSubCategory)
admin.site.register(DiseaseCode, DiseaseCodeAdmin)  # 커스터마이징한 DiseaseCode 등록

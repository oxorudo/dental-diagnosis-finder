from django.contrib import admin
from .models import (
    DentalClaim
)


class DiseaseCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "level",
        "parent",
    )  # 관리자 페이지에서 보여줄 필드들


# 모델을 관리자 페이지에 등록
admin.site.register(DentalClaim)

from django.urls import path
from . import views

urlpatterns = [
    # path("", views.index, name="index"),  # 기본 검색 페이지
    # path("search/", views.search, name="search"),  # 검색 페이지 추가
    path("", views.search_view, name="home"),
    path("search/", views.search_view, name="search_view"),
    path("detail-action/", views.detail_action, name="detail_action"),
]

from django.urls import path
from . import views

urlpatterns = [
    # path("", views.index, name="index"),  # 기본 검색 페이지
    # path("search/", views.search, name="search"),  # 검색 페이지 추가
    path('search/', views.search_view, name='search_view'),
    path('autocomplete/', views.autocomplete_view, name='autocomplete_view'),
]

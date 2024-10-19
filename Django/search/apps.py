from django.apps import AppConfig
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from .utils.GoogleSheet import get_sheet_data, get_url, find_key_path
from .utils.QueryCorrection import HangulSearch       
from .utils.hierarchy import build_hierarchy

class SearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "search"
    
    def ready(self):
        global global_sheet_data
        global global_searcher
        global global_url
        global global_hierarchy_structure  # 전역 변수 추가
        global global_api_key_path
        
        # 서버 시작 시 데이터 불러오기
        global_api_key_path = find_key_path()
        
        # 구글 스프레드시트 불러오기
        global_sheet_data = get_sheet_data(global_api_key_path)
        
        # 세부 청부 항목 URL 불러오기(구글 스프레드 시트)
        global_url = get_url(global_api_key_path)
        
        # 검색 알고리즘
        global_searcher = HangulSearch(global_sheet_data)

        # 전체 계층 구조를 서버 시작 시 한 번만 로드
        global_hierarchy_structure = build_hierarchy(global_sheet_data)  # 전체 계층 구조를 전역 변수에 저장
    
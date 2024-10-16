from django.apps import AppConfig
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from .utils.GoogleSheet import get_sheet_data,get_url,find_key_path
from .utils.QueryCorrection import HangulSearch

class SearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "search"
    
    def ready(self):
        global global_sheet_data
        global global_searcher
        global global_url
        # 서버 시작 시 데이터 불러오기
        api_key_path = find_key_path()
        global_sheet_data = get_sheet_data(api_key_path)
        global_searcher = HangulSearch(global_sheet_data)
        global_url = get_url(api_key_path)

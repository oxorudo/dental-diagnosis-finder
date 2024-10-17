from django.apps import AppConfig

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from .utils.GoogleSheet import get_sheet_data
from .utils.QueryCorrection import HangulSearch

global_sheet_data = None  # 전역 변수로 선언

class SearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "search"
    
    def ready(self):
        global global_sheet_data
        global global_searcher
        # 서버 시작 시 데이터 불러오기
        global_sheet_data = get_sheet_data("/Users/mane/Documents/dental-diagnosis-finder/NLP/key.json")
        global_searcher = HangulSearch(global_sheet_data)

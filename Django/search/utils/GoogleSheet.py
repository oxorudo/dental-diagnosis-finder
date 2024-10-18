import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def get_sheet_data(
    api_key_path: str, 
    sheet_url :str = "https://docs.google.com/spreadsheets/d/1PzFuHuF2DvMPdSI-TK4Kq5LjPwyGzIxH3Q0Drnqft20/edit?usp=sharing",
    sheet_name: str = "상병 Category의 사본"
    )-> pd.DataFrame:
    """
    Google 스프레드시트에서 데이터를 불러와 Pandas DataFrame으로 반환하는 함수.

    Args:
        api_key_path (str): Google API 인증에 필요한 JSON 파일 경로.
        sheet_url (str, optional): 불러올 Google 스프레드시트의 URL. 기본값은 특정 스프레드시트 URL.
        sheet_name (str, optional): 불러올 시트의 이름. 기본값은 '상병 Category의 사본'.

    Returns:
        pd.DataFrame: 스프레드시트의 데이터를 담은 Pandas DataFrame 객체.
        
    Example:
        df = get_sheet_data("path_to_api_key.json")
    """
    
    # Google Sheets API 인증 및 접근
    scope = ["https://spreadsheets.google.com/feeds", ]

    credits = ServiceAccountCredentials.from_json_keyfile_name(api_key_path, scope)
    gc = gspread.authorize(credits)

    # 스프레드시트 URL 설정
    spreadsheet_url = sheet_url

    # URL을 통해 스프레드시트 열기
    doc = gc.open_by_url(spreadsheet_url)

    # 특정 시트 선택 (사본 페이지)
    sheet = doc.worksheet(sheet_name)

    # 시트의 모든 데이터를 가져오기 (2D 리스트 형태로 가져옴)
    data = sheet.get_all_values()

    # 데이터프레임으로 변환
    df = pd.DataFrame(data[1:], columns=data[0])  # 첫 번째 행은 컬럼명으로 설정
    return df


def get_url()->pd.DataFrame:
    sheet_data = get_sheet_data(
            api_key_path='D:\\workspace\\dental-diagnosis-finder\\NLP\\key.json',  # 자신의 API 키 경로
            sheet_url='https://docs.google.com/spreadsheets/d/1PzFuHuF2DvMPdSI-TK4Kq5LjPwyGzIxH3Q0Drnqft20/edit?usp=sharing',
            sheet_name='행위별 Category'
        )
    
    return sheet_data



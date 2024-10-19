import re
import pandas as pd

# 정규 표현식 사전 컴파일
code_cleaner = re.compile(r"\x08")

# 불완전 상병 코드와 상병명에서 값을 빠르게 정리하는 함수
def clean_code(code):
    return code_cleaner.sub("", code.strip())

def clean_name(name):
    return code_cleaner.sub("", name.strip())

# apply를 활용한 벡터화 방식으로 코드 최적화
def get_disease_hierarchy(sheet_data: pd.DataFrame):
    hierarchy = {}
    
    # 코드와 이름을 벡터화하여 처리
    sheet_data['clean_code'] = sheet_data['불완전 상병 코드'].apply(clean_code)
    sheet_data['clean_name'] = sheet_data['불완전 상병명'].apply(clean_name)
    
    # 코드가 ".~"로 끝나는 행들만 필터링
    filtered_data = sheet_data[sheet_data['clean_code'].str.endswith('.~')]

    # 대분류를 저장
    hierarchy = {row.clean_code: {"name": row.clean_name, "children": {}} for row in filtered_data.itertuples(index=False)}
    
    return hierarchy

def get_middle_categories(hierarchy, sheet_data: pd.DataFrame):
    middle_categories = {}

    for row in sheet_data.itertuples(index=False):
        code = row.clean_code
        name = row.clean_name

        # 코드 길이 확인 및 중분류 조건 확인
        if len(code) >= 2 and (
            (code[-2].isdigit() and code[-1] == "~") or 
            (code.split(".")[-1].isdigit() and len(code.split(".")[-1]) == 1)
        ):
            cleaned_code = code.rstrip("~")
            parent_code = code.rsplit(".", 1)[0] + ".~"  # 대분류 코드

            if parent_code not in middle_categories:
                middle_categories[parent_code] = {
                    "name": hierarchy.get(parent_code, {}).get("name", ""),
                    "children": {},
                }
            middle_categories[parent_code]["children"][cleaned_code] = {
                "name": name,
                "children": {},  # 하위분류를 위한 children 초기화
            }

    return middle_categories

def get_sub_categories(middle_categories, sheet_data: pd.DataFrame):
    for row in sheet_data.itertuples(index=False):
        code = row.clean_code
        name = row.clean_name

        # 하위분류 코드 확인 (숫자가 2자리 또는 3자리인 경우)
        if code.split(".")[-1].isdigit():
            code_length = len(code.split(".")[-1])

            if code_length == 2:
                parent_code = code[:-1]
            elif code_length == 3:
                parent_code = code[:-2]
            else:
                continue  # 조건에 맞지 않으면 패스

            for major_code, major_data in middle_categories.items():
                if parent_code in major_data["children"]:
                    major_data["children"][parent_code]["children"][code] = {
                        "name": name,
                        "type": "sub",
                    }
                    major_data["children"][parent_code]["has_subcategories"] = True

    return middle_categories

def build_hierarchy(sheet_data: pd.DataFrame):
    # 미리 데이터 정리 후, 한번에 처리
    hierarchy = get_disease_hierarchy(sheet_data)
    middle_categories = get_middle_categories(hierarchy, sheet_data)
    sub_categories = get_sub_categories(middle_categories, sheet_data)

    # 최종 계층 구조 생성
    full_hierarchy = {parent_code: {
        "name": middle_category["name"],
        "children": middle_category["children"],
    } for parent_code, middle_category in middle_categories.items()}

    return full_hierarchy

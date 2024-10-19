import re
import pandas as pd
def get_disease_hierarchy(sheet_data: pd.DataFrame):
    # Google Sheets에서 데이터를 불러옵니다.
    hierarchy = {}

    for index, row in sheet_data.iterrows():
        code = re.sub(r"\x08", "", row['불완전 상병 코드'].strip())
        name = re.sub(r"\x08", "", row['불완전 상병명'].strip())

        if code.endswith(".~"):
            hierarchy[code] = {"name": name, "children": {}}
    return hierarchy

def get_middle_categories(hierarchy, sheet_data: pd.DataFrame):
    middle_categories = {}

    for index, row in sheet_data.iterrows():
        code = re.sub(r"\x08", "", row['불완전 상병 코드'].strip())
        name = re.sub(r"\x08", "", row['불완전 상병명'].strip())

        # 코드 길이 확인
        if len(code) < 2:
            continue  # 코드가 2자리 미만이면 건너뛰기

        # 중분류 코드 확인 (K00.0~, K00.1 형식)
        if (code[-2].isdigit() and code[-1] == "~") or (
            code.split(".")[-1].isdigit() and len(code.split(".")[-1]) == 1
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

    for index, row in sheet_data.iterrows():
        code = re.sub(r"\x08", "", row['불완전 상병 코드'].strip())
        name = re.sub(r"\x08", "", row['불완전 상병명'].strip())

        # 하위분류 코드 확인 (숫자가 2자리인 경우)
        if code.split(".")[-1].isdigit() and len(code.split(".")[-1]) == 2:
            parent_code = code[:-1]  # 대분류가 아닌 중분류 코드로 설정
            for major_code, major_data in middle_categories.items():
                if parent_code in major_data["children"]:  # 중분류가 존재하는 경우
                    major_data["children"][parent_code]["children"][code] = {
                        "name": name,
                        "type": "sub",
                    }
                    major_data["children"][parent_code]["has_subcategories"] = True

        if code.split(".")[-1].isdigit() and len(code.split(".")[-1]) == 3:
            parent_code = code[:-2]  # 대분류가 아닌 중분류 코드로 설정
            for major_code, major_data in middle_categories.items():
                if parent_code in major_data["children"]:  # 중분류가 존재하는 경우
                    major_data["children"][parent_code]["children"][code] = {
                        "name": name,
                        "type": "sub",
                    }
                    major_data["children"][parent_code]["has_subcategories"] = True

    return middle_categories

def build_hierarchy(sheet_data: pd.DataFrame):
    hierarchy = get_disease_hierarchy(sheet_data)
    middle_categories = get_middle_categories(hierarchy,sheet_data)
    sub_categories = get_sub_categories(middle_categories,sheet_data)

    # 최종 계층 구조 생성
    full_hierarchy = {}
    for parent_code, middle_category in middle_categories.items():
        full_hierarchy[parent_code] = {
            "name": middle_category["name"],
            "children": middle_category["children"],
        }
        if parent_code in sub_categories:
            full_hierarchy[parent_code]["children"].update(
                sub_categories[parent_code]["children"]
            )

    return full_hierarchy
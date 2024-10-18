import json
from django.http import JsonResponse
from django.shortcuts import render
from Django.search.utils.category_colors import CATEGORY_COLORS
from .models import DentalClaim
from search.apps import global_searcher, global_url, global_sheet_data
from django.views.decorators.csrf import csrf_exempt
import re

def search_view(request):
    query = request.GET.get("q", "").strip()  # 검색어 가져오기
    results = []
    
    # 전체 계층 구조 가져오기
    full_hierarchy = build_hierarchy() 

    if query:
        search_results = global_searcher.search_df_with_options(query)
        
        # 검색 결과 가공
        for row in search_results.values.tolist():
            split_categories = row[2].split(' | ') if row[2] else []
            split_details = row[3].split(' | ') if row[3] else []

            # 각 카테고리에 색상 추가
            categories_with_colors = [
                {'name': category, 'color': CATEGORY_COLORS.get(category, '#6c757d')}
                for category in split_categories
            ]

            # 결과에 카테고리와 세부 청구 항목 추가
            results.append({
                'code': row[0],
                'name': row[1],
                'categories': categories_with_colors,  # 카테고리와 색상 정보 함께 저장
                'split_details': split_details
            })
            
    context = {
        "results": results,  # 검색 결과
        "query": query,  # 검색어
        "full_hierarchy": full_hierarchy,  # 사이드바에 필요한 전체 계층 구조
    }

    return render(request, "search.html", context)


def get_disease_hierarchy():
    claims = DentalClaim.objects.all()
    hierarchy = {}

    for claim in claims:
        code = re.sub(r"\x08", "", claim.incomplete_disease_code.strip())
        name = re.sub(r"\x08", "", claim.incomplete_disease_name.strip())

        if code.endswith(".~"):
            hierarchy[code] = {"name": name, "children": {}}

    return hierarchy


def get_middle_categories(hierarchy):
    claims = DentalClaim.objects.all()
    middle_categories = {}

    for claim in claims:
        code = re.sub(r"\x08", "", claim.incomplete_disease_code.strip())
        name = re.sub(r"\x08", "", claim.incomplete_disease_name.strip())

        # 코드 길이 확인
        if len(code) < 2:
            continue  # 코드가 2자리 미만이면 건너뛰기

        # 중분류 코드 확인 (K00.0~, K00.1 형식)
        if (code[-2].isdigit() and code[-1] == "~") or (
            code.split(".")[-1].isdigit() and len(code.split(".")[-1]) == 1
        ):
            # 물결표시가 있는 경우 제거
            cleaned_code = code.rstrip("~")
            parent_code = code.rsplit(".", 1)[0] + ".~"  # 대분류 코드
            # 대분류가 존재하지 않으면 추가
            if parent_code not in middle_categories:
                middle_categories[parent_code] = {
                    "name": hierarchy.get(parent_code, {}).get(
                        "name", ""
                    ),  # 대분류 이름 가져오기
                    "children": {},
                }
            # 중분류 추가
            middle_categories[parent_code]["children"][cleaned_code] = {
                "name": name,
                "children": {},  # 하위분류를 위한 children 초기화
            }

    return middle_categories


def get_sub_categories(middle_categories):
    claims = DentalClaim.objects.all()

    for claim in claims:
        code = re.sub(r"\x08", "", claim.incomplete_disease_code.strip())
        name = re.sub(r"\x08", "", claim.incomplete_disease_name.strip())

        # 하위분류 코드 확인 (숫자가 2자리인 경우)
        if code.split(".")[-1].isdigit() and len(code.split(".")[-1]) == 2:
            # 하위분류는 중분류 코드에 속해야 함
            # 부모 코드는 마침표 이후 첫 번째 숫자를 기준으로 중분류 코드로 판단
            parent_code = code[:-1]  # 대분류가 아닌 중분류 코드로 설정
            # 중분류 코드가 middle_categories에 있는지 확인
            for major_code, major_data in middle_categories.items():
                if parent_code in major_data["children"]:  # 중분류가 존재하는 경우
                    # 중분류에 하위분류 추가
                    major_data["children"][parent_code]["children"][code] = {
                        "name": name,
                        "type": "sub",
                    }
                    # 하위분류가 있음을 표시
                    major_data["children"][parent_code]["has_subcategories"] = True

        if code.split(".")[-1].isdigit() and len(code.split(".")[-1]) == 3:
            parent_code = code[:-2]  # 대분류가 아닌 중분류 코드로 설정
            # 중분류 코드가 middle_categories에 있는지 확인
            for major_code, major_data in middle_categories.items():
                if parent_code in major_data["children"]:  # 중분류가 존재하는 경우
                    # 중분류에 하위분류 추가
                    major_data["children"][parent_code]["children"][code] = {
                        "name": name,
                        "type": "sub",
                    }
                    # 하위분류가 있음을 표시
                    major_data["children"][parent_code]["has_subcategories"] = True

    return middle_categories


def build_hierarchy():
    hierarchy = get_disease_hierarchy()
    middle_categories = get_middle_categories(hierarchy)
    sub_categories = get_sub_categories(middle_categories)

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


@csrf_exempt  # You might want to add CSRF protection in production
def detail_action(request):
    if request.method == "POST":
        data = json.loads(request.body)
        detail = data.get("detail")
        
        sheet_data = global_url  # Replace with your actual data source

        # Search for matching detail
        matching_row = sheet_data[sheet_data["세부 청구 항목 (키워드)"] == detail]
        if not matching_row.empty:
            link = matching_row.iloc[0]["URL(tripletclover.com)"]
            return JsonResponse({"link": link})
        else:
            return JsonResponse({"error": "No matching link found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)


# views.py
from django.shortcuts import render


def add_view(request):
    # 추가 로직 구현
    return render(request, "add_template.html")

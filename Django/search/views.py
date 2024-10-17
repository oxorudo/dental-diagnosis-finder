import json
from django.http import JsonResponse
from django.shortcuts import render

from .models import DentalClaim
from transformers import AutoTokenizer, AutoModel
import torch
import difflib
from search.apps import global_searcher,global_url
from django.views.decorators.csrf import csrf_exempt
from Django.search.utils.GoogleSheet import get_sheet_data


# KoELECTRA 모델 및 토크나이저 로드
model_name = "jhgan/ko-sroberta-multitask"
tokenizer = AutoTokenizer.from_pretrained(model_name, clean_up_tokenization_spaces=True)
model = AutoModel.from_pretrained(model_name)



# 텍스트를 임베딩으로 변환하는 함수
def get_embeddings(texts):
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].numpy()  # [CLS] 토큰 벡터만 사용

# 오탈자 교정 함수
def correct_typo(input_word, dictionary):
    closest_matches = difflib.get_close_matches(input_word, dictionary, n=3, cutoff=0.5)
    if closest_matches:
        corrected_word = closest_matches[0]  # 가장 유사한 단어 선택
        suggestions = closest_matches  # 제안 목록
    else:
        corrected_word = input_word
        suggestions = []
    return corrected_word, suggestions


def search_view(request):
    query = request.GET.get("q", "").strip()
    results = []
    corrected_query = None

    # full_hierarchy는 항상 가져오기 (검색과 무관하게)
    full_hierarchy = build_hierarchy()  # 전체 계층 구조 가져오기

    if query:
        # 검색어가 있을 때만 검색을 수행
        search_results = global_searcher.search_df_with_options(query)
        results = search_results.values.tolist()

    context = {
        "results": results,              # 검색 결과
        "query": query,                  # 검색어
        "full_hierarchy": full_hierarchy  # 사이드바에 필요한 전체 계층 구조
    }
    print(results)

    return render(request, "search.html", context)

def get_disease_hierarchy():
    claims = DentalClaim.objects.all()
    hierarchy = {}

    for claim in claims:
        code = claim.incomplete_disease_code
        name = claim.incomplete_disease_name

        if code.endswith(".~"):
            hierarchy[code] = {"name": name, "children": {}}

    return hierarchy


def get_middle_categories(hierarchy):
    claims = DentalClaim.objects.all()
    middle_categories = {}

    for claim in claims:
        code = claim.incomplete_disease_code
        name = claim.incomplete_disease_name

        # 코드 길이 확인
        if len(code) < 2:
            continue  # 코드가 2자리 미만이면 건너뛰기

        # 중분류 코드 확인 (K00.0~, K00.1 형식)
        if (code[-2].isdigit() and code[-1] == "~") or (
            code.split(".")[-1].isdigit() and len(code.split(".")[-1]) == 1
        ):
            parent_code = code.rsplit(".", 1)[0] + "."  # 대분류 코드
            if parent_code not in middle_categories:
                middle_categories[parent_code] = {
                    "name": hierarchy.get(parent_code, {}).get("name", ""),
                    "children": {},
                }
            middle_categories[parent_code]["children"][code] = {
                "name": name,
                "children": {},  # 하위분류를 위한 children 초기화
            }

    return middle_categories


def get_sub_categories(middle_categories):
    claims = DentalClaim.objects.all()

    for claim in claims:
        code = claim.incomplete_disease_code
        name = claim.incomplete_disease_name

        # 하위분류 코드 확인 (숫자가 2자리 또는 3자리인 경우)
        if code.split(".")[-1].isdigit() and len(code.split(".")[-1]) in {2, 3}:
            parent_code = ".".join(code.split(".")[:-1]) + "."  # 중분류 코드
            if parent_code in middle_categories:  # 중분류가 존재하는 경우
                # 중분류에 하위분류 추가
                middle_categories[parent_code]["children"][code] = {"name": name, 'type': 'sub'}

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

@csrf_exempt  # CSRF 검사를 비활성화할 수 있습니다. 또는 POST 요청 시 AJAX에 CSRF 토큰을 포함해야 합니다.
def detail_action(request):
    if request.method == 'POST':
        # 클라이언트에서 받은 JSON 데이터를 파싱
        data = json.loads(request.body)
        detail = data.get('detail')

        sheet_data = global_url
        
        matching_row = sheet_data[sheet_data['세부 청구 항목 (키워드)'] == detail]
        if not matching_row.empty:
            link = matching_row.iloc[0]['URL  (tripletclover.com)']  # 첫 번째 일치 항목의 URL 반환
            return JsonResponse({'link': link})
        else:
            return JsonResponse({'error': 'No matching link found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)
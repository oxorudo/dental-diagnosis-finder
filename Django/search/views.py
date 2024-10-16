from django.http import JsonResponse
from django.shortcuts import render
from .models import DentalClaim
from .forms import SearchForm
from transformers import AutoTokenizer, AutoModel
import torch
import difflib
from django.db.models import Q
from django.core.cache import cache


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
    form = SearchForm()
    data = []
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()  # 검색어 가져오기
        print(query)
        if not query:
            # 검색어가 없으면 빈 리스트를 반환
            return render(request, 'search.html', {'results': [], 'query': query})

        # 검색어가 있을 때 필터링
        results = DentalClaim.objects.filter(
            Q(incomplete_disease_code__icontains=query) |
            Q(incomplete_disease_name__icontains=query) |
            Q(claim_category__icontains=query) |
            Q(claim_detail__icontains=query)
        )
        print(f"Results: {list(results)}")
        
        # QuerySet을 딕셔너리 형태로 변환
        data = list(results.values(
            'incomplete_disease_code', 'incomplete_disease_name', 'claim_category', 'claim_detail'
        ))

    # 결과와 검색어를 템플릿으로 전달
    return render(request, 'search.html', {'results': results, 'query': query,'data' : data})

def autocomplete_view(request):
    query = request.GET.get('q', '')
    if query:
        suggestions = DentalClaim.objects.filter(
            Q(incomplete_disease_code__icontains=query) |
            Q(incomplete_disease_name__icontains=query)
        ).values_list('incomplete_disease_name', flat=True).distinct()  # 중복 제거
    else:
        suggestions = []

    return JsonResponse(list(suggestions), safe=False)


# def search(request):
#     keyword = request.GET.get("keyword", "")

#     # 가능한 모든 단어 데이터 리스트
#     disease_codes = list(DiseaseCode.objects.values_list("name", flat=True))
#     insurance_categories = list(
#         InsuranceCategory.objects.values_list("name", flat=True)
#     )
#     insurance_sub_categories = list(
#         InsuranceSubCategory.objects.values_list("name", flat=True)
#     )

#     # 오탈자 교정을 위한 전체 단어 리스트
#     word_score_table = disease_codes + insurance_categories + insurance_sub_categories

#     # 오탈자 교정된 추천 검색어 리스트
#     corrected_keyword, suggested_keywords = correct_typo(keyword, word_score_table)

#     # 검색 결과 필터링 (교정된 검색어를 사용)
#     disease_codes_result = DiseaseCode.objects.filter(name__icontains=corrected_keyword)

#     # context에 모든 검색 결과와 추천 검색어 전달
#     context = {
#         "disease_codes": disease_codes_result,
#         "suggested_keywords": suggested_keywords,  # 추천 검색어 전달
#         "keyword": keyword,  # 원래 검색어도 전달
#         "corrected_keyword": corrected_keyword,  # 교정된 검색어 전달
#         "disease_categories_list": DiseaseCode.objects.prefetch_related(
#             "children"
#         ).filter(
#             parent=None
#         ),  # 모든 대분류
#     }

#     return render(request, "results.html", context)


# def index(request):
#     # 모든 대분류를 가져옵니다.
#     disease_codes = DiseaseCode.objects.prefetch_related("children").filter(
#         level="대분류"
#     )  # 대분류 필터링

#     return render(request, "index.html", {"main_disease_codes": disease_codes})

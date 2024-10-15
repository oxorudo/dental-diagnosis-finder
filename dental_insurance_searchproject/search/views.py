from django.shortcuts import render
from .models import (
    InsuranceCategory,
    InsuranceSubCategory,
    DiseaseDetailCode,
    DiseaseCategory,
    DiseaseSubCategory,
)
from transformers import AutoTokenizer, AutoModel
import faiss
import torch
from rapidfuzz import process, fuzz
from soynlp.word import WordExtractor
import difflib

# KoELECTRA 모델 및 토크나이저 로드
model_name = "jhgan/ko-sroberta-multitask"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)


# 텍스트를 임베딩으로 변환하는 함수
def get_embeddings(texts):
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].numpy()  # [CLS] 토큰 벡터만 사용


# FAISS 인덱스 생성 및 데이터 추가
def build_faiss_index(data):
    embeddings = get_embeddings(data)
    dimension = embeddings.shape[1]  # KoELECTRA 임베딩 차원
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)  # 데이터베이스 임베딩 추가
    return index, embeddings


# 유사 항목 찾기 (FAISS 및 코사인 유사도)
def search_similar(query, data, index, embeddings, top_k=5):
    query_embedding = get_embeddings([query])
    distances, indices = index.search(query_embedding, top_k)
    similar_items = [data[i] for i in indices[0]]  # 상위 유사 항목 추출
    return similar_items


# 사전 구축 (기존 데이터로)
def build_dictionary(data):
    word_extractor = WordExtractor()
    word_extractor.train(data)
    word_score_table = word_extractor.extract()
    return word_score_table


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


def search(request):
    keyword = request.GET.get("keyword", "").strip()  # 검색어를 받아오고 공백 제거

    # DiseaseDetailCode와 InsuranceCategory에서 가능한 모든 단어 데이터 리스트
    disease_names = list(
        DiseaseDetailCode.objects.values_list("detail_name", flat=True)
    )
    insurance_categories = list(
        InsuranceCategory.objects.values_list("name", flat=True)
    )
    insurance_sub_categories = list(
        InsuranceSubCategory.objects.values_list("name", flat=True)
    )
    disease_categories = list(
        DiseaseCategory.objects.values_list("incomplete_name", flat=True)
    )
    disease_sub_categories = list(
        DiseaseSubCategory.objects.values_list("name", flat=True)
    )

    # 오탈자 교정을 위한 전체 단어 리스트
    word_score_table = (
        disease_names
        + insurance_categories
        + insurance_sub_categories
        + disease_categories
        + disease_sub_categories
    )

    # 오탈자 교정된 추천 검색어 리스트
    corrected_keyword, suggested_keywords = correct_typo(keyword, word_score_table)

    # 검색 결과 필터링 (교정된 검색어를 사용)
    insurance_categories_result = InsuranceCategory.objects.filter(
        name__icontains=corrected_keyword
    )
    insurance_sub_categories_result = InsuranceSubCategory.objects.filter(
        name__icontains=corrected_keyword
    )
    disease_categories_result = DiseaseCategory.objects.filter(
        incomplete_name__icontains=corrected_keyword
    )
    disease_sub_categories_result = DiseaseSubCategory.objects.filter(
        name__icontains=corrected_keyword
    )
    disease_codes_result = DiseaseDetailCode.objects.filter(
        detail_name__icontains=corrected_keyword
    )

    # context에 모든 검색 결과와 추천 검색어 전달
    context = {
        "insurance_categories": insurance_categories_result,
        "insurance_sub_categories": insurance_sub_categories_result,
        "disease_categories": disease_categories_result,
        "disease_sub_categories": disease_sub_categories_result,
        "disease_codes": disease_codes_result,
        "suggested_keywords": suggested_keywords,  # 추천 검색어 전달
        "keyword": keyword,  # 원래 검색어도 전달
        "corrected_keyword": corrected_keyword,  # 교정된 검색어 전달
        "disease_categories_list": DiseaseCategory.objects.prefetch_related(
            "diseasesubcategory_set"
        ).all(),  # 모든 대분류 및 중분류 리스트
    }

    return render(request, "results.html", context)


def index(request):
    # 모든 대분류 및 중분류를 가져옵니다.
    disease_categories = DiseaseCategory.objects.prefetch_related(
        "diseasesubcategory_set"
    ).all()  # 대분류와 중분류 연결
    main_disease_codes = []

    # 대분류와 그에 속한 중분류 리스트 생성
    for category in disease_categories:
        subcategories = (
            category.diseasesubcategory_set.all()
        )  # 해당 대분류의 중분류 가져오기
        main_disease_codes.append(
            {
                "code": category.incomplete_code,
                "name": category.incomplete_name,
                "subcategories": subcategories,  # 중분류 추가
            }
        )

    return render(request, "index.html", {"main_disease_codes": main_disease_codes})

from django.shortcuts import render
from .models import (
    InsuranceCategory,
    InsuranceSubCategory,
    DiseaseDetailCode,
    DiseaseCategory,
    DiseaseSubCategory,
)
from fuzzywuzzy import fuzz


# 오탈자 교정 함수 (다중 추천 기능 추가)
def get_similar_choices(query, choices, threshold=80):
    """
    주어진 선택 항목에서 사용자의 입력(query)에 유사한 여러 항목을 반환
    :param query: 사용자 검색어
    :param choices: 데이터베이스에서 가져온 항목들 (예: 상병명, 카테고리명 등)
    :param threshold: 유사도 점수의 기준 (기본 80 이상)
    :return: 유사한 항목들의 리스트
    """
    similar_choices = []
    for choice in choices:
        score = fuzz.ratio(query.lower(), choice.lower())  # 유사도 계산
        if score >= threshold:  # 설정한 유사도 기준을 넘는 항목만 추천
            similar_choices.append(choice)
    return similar_choices


def search(request):
    keyword = request.GET.get("keyword", "")  # GET 요청에서 검색어를 받음

    # 데이터베이스에서 카테고리 및 상병명 리스트 가져오기
    disease_names = DiseaseDetailCode.objects.values_list("detail_name", flat=True)
    insurance_categories = InsuranceCategory.objects.values_list("name", flat=True)

    # 오탈자 교정된 상병명과 보험 카테고리명 (유사 항목 추천)
    similar_disease_names = get_similar_choices(keyword, disease_names)
    similar_insurance_categories = get_similar_choices(keyword, insurance_categories)

    # 보험 카테고리에서 검색
    insurance_categories = InsuranceCategory.objects.filter(name__icontains=keyword)
    insurance_sub_categories = InsuranceSubCategory.objects.filter(
        name__icontains=keyword
    )

    # 상병코드 카테고리에서 검색
    disease_categories = DiseaseCategory.objects.filter(
        incomplete_name__icontains=keyword
    )
    disease_sub_categories = DiseaseSubCategory.objects.filter(name__icontains=keyword)

    # 하위분류 상병코드가 있는 경우와 없는 경우 처리
    disease_codes = DiseaseDetailCode.objects.filter(detail_name__icontains=keyword)

    context = {
        "insurance_categories": insurance_categories,
        "insurance_sub_categories": insurance_sub_categories,
        "disease_categories": disease_categories,
        "disease_sub_categories": disease_sub_categories,
        "disease_codes": disease_codes,
        "similar_disease_names": similar_disease_names,
        "similar_insurance_categories": similar_insurance_categories,
        "keyword": keyword,
    }
    return render(request, "results.html", context)


def index(request):
    # 대분류 상병코드 + 상병명 리스트
    main_disease_codes = [
        {"code": "K00.~", "name": "치아 발육 및 맹출 장애"},
        {"code": "K01.~", "name": "매몰치 및 매복치"},
        {"code": "K02.~", "name": "치아 우식"},
        {"code": "K03.~", "name": "마모 등 치아 경조직 질환"},
        {"code": "K04.~", "name": "치수 및 근단"},
        {"code": "K05.~", "name": "치은염 및 치주질환"},
        {"code": "K06.~", "name": "잇몸 및 무치성 치조융기의 기타 장애"},
        {"code": "K07.~", "name": "치아얼굴이상 [부정교합 포함]"},
        {"code": "K08.~", "name": "치아 및 지지구조의 기타 장애"},
        {"code": "K10.~", "name": "턱의 기타 질환"},
        {"code": "K11.~", "name": "침샘의 질환"},
        {"code": "K12.~", "name": "구내염 및 관련 병변"},
        {"code": "K13.~", "name": "입술 및 구강점막의 기타 질환"},
        {"code": "S00.~", "name": "머리의 표재성 손상"},
        {"code": "S01.~", "name": "머리의 열린상처"},
        {"code": "S02.~", "name": "두개골 및 안면골의 골절"},
        {"code": "S03.~", "name": "머리의 관절 및 인대의 탈구, 염좌 및 긴장"},
        {"code": "S04.~", "name": "뇌신경의 손상"},
        {"code": "B00.~", "name": "헤르페스바이러스 감염"},
        {"code": "D10.~", "name": "입 인두의 양성 신생물"},
        {"code": "K29.0~", "name": "위염 및 십이지장염"},
        {"code": "Q38.~", "name": "혀입인두의 선천기형"},
        {"code": "기타", "name": "기타 상병명"},
    ]

    return render(request, "index.html", {"main_disease_codes": main_disease_codes})

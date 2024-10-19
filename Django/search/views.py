import json
from django.http import JsonResponse
from django.shortcuts import render
from .utils.category_colors import CATEGORY_COLORS
from .apps import global_searcher, global_url, global_hierarchy_structure
from django.views.decorators.csrf import csrf_exempt


def search_view(request):
    query = request.GET.get("q", "").strip()  # 검색어 가져오기
    results = []

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
        # "full_hierarchy": global_hierarchy_structure,  # 사이드바에 필요한 전체 계층 구조
    }

    return render(request, "search.html", context)





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

def add_view(request):
    # 추가 로직 구현
    return render(request, "add_template.html")

import json
from django.http import JsonResponse
from django.shortcuts import render
from .utils.category_colors import CATEGORY_COLORS
from .apps import global_searcher, global_url
from django.views.decorators.csrf import csrf_exempt    

def search_view(request):
    query = request.GET.get("q", "").strip()  # 검색어 가져오기
    results = []

    print(f"Search Query: '{query}'")  # 디버깅: 검색어 출력

    if query:
        search_results = global_searcher.search_df_with_options(query)
        
        # 검색 결과 가공
        for row in search_results.values.tolist():
            split_categories = row[2].split(' | ') if row[2] else []
            split_details = row[3].split(' | ') if row[3] else []

            
            # '대분류/중분류'는 제외하고, '하위분류'만 결과에 포함 (코드가 '~'로 끝나지 않으면)
            if not row[0].endswith('~'):
                categories_with_colors = [
                    {'name': category, 'color': CATEGORY_COLORS.get(category, '#6c757d')}
                    for category in split_categories
                ]

                results.append({
                    'code': row[0],  # 원래 코드 값을 유지
                    'name': row[1],
                    'categories': categories_with_colors,
                    'split_details': split_details
                })

    # AJAX 요청 확인
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "GET":
        return JsonResponse({"results": results, "query": query})

    context = {
        "results": results,
        "query": query,
    }
    return render(request, "index.html", context)


@csrf_exempt  # You might want to add CSRF protection in production
def detail_action(request):
    if request.method == "POST":
        data = json.loads(request.body)
        detail = data.get("detail")
        
        url_sheet_data = global_url  # Replace with your actual data source

        # Search for matching detail
        matching_row = url_sheet_data[url_sheet_data["세부 청구 항목 (키워드)"] == detail]
        if not matching_row.empty:
            link = matching_row.iloc[0]["URL(tripletclover.com)"]
            return JsonResponse({"link": link})
        else:
            return JsonResponse({"error": "No matching link found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)

def add_view(request):
    # 추가 로직 구현
    return render(request, "add_template.html")


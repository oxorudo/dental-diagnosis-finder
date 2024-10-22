import json
from django.http import JsonResponse
from django.shortcuts import render
from .utils.category_colors import CATEGORY_COLORS
from .apps import global_searcher, global_url
from django.views.decorators.csrf import csrf_exempt


def search_view(request):
    query = request.GET.get("q", "").strip()  # 검색어 가져오기
    results = []

    if query:
        search_results = global_searcher.search_df_with_options(query)

        # 검색 결과 가공
        for row in search_results.values.tolist():
            split_categories = row[2].split(" | ") if row[2] else []
            split_details = row[3].split(" | ") if row[3] else []

            # 각 카테고리에 색상 추가
            categories_with_colors = [
                {"name": category, "color": CATEGORY_COLORS.get(category, "#6c757d")}
                for category in split_categories
            ]

            # 결과에 카테고리와 세부 청구 항목 추가
            results.append(
                {
                    "code": row[0],
                    "name": row[1],
                    "categories": categories_with_colors,  # 카테고리와 색상 정보 함께 저장
                    "split_details": split_details,
                }
            )

    # AJAX 요청 확인 (is_ajax() 대신 헤더 확인)
    if (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        and request.method == "GET"
    ):
        return JsonResponse({"results": results, "query": query})  # JSON 응답 반환

    context = {
        "results": results,  # 검색 결과
        "query": query,  # 검색어
    }
    return render(request, "index.html", context)


@csrf_exempt  # You might want to add CSRF protection in production
def detail_action(request):
    if request.method == "POST":
        data = json.loads(request.body)
        detail = data.get("detail")

        url_sheet_data = global_url  # Replace with your actual data source

        # Search for matching detail
        matching_row = url_sheet_data[
            url_sheet_data["세부 청구 항목 (키워드)"] == detail
        ]
        if not matching_row.empty:
            link = matching_row.iloc[0]["URL(tripletclover.com)"]
            return JsonResponse({"link": link})
        else:
            return JsonResponse({"error": "No matching link found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)

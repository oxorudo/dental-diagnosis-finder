from .utils.hierarchy import build_hierarchy  # hierarchy.py에서 가져오기

def full_hierarchy_processor(request):
    full_hierarchy = build_hierarchy()  # 계층 구조 생성
    return {
        'full_hierarchy': full_hierarchy  # 템플릿에서 full_hierarchy 사용 가능
    }

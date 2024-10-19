from ..apps import global_hierarchy_structure

def full_hierarchy_processor(request):
    full_hierarchy = global_hierarchy_structure
    return {
        'full_hierarchy': full_hierarchy  # 템플릿에서 full_hierarchy 사용 가능
    }

from django.shortcuts import render
from send_post.models import StudyMaterialPost
from django.core.paginator import Paginator


def learn_post(request):
    # 获取搜索关键词
    search_query = request.GET.get('search', '')
    
    # 获取所有学习资料帖子
    posts = StudyMaterialPost.objects.all()
    
    # 如果有搜索关键词，过滤标题
    if search_query:
        posts = posts.filter(title__icontains=search_query)
    
    # 按创建时间倒序排序
    posts = posts.order_by('-created_time')
    
    # 分页处理
    paginator = Paginator(posts, 10)  # 每页显示10条
    page_number = request.GET.get('page', 1)
    try:
        page_number = int(page_number)
    except ValueError:
        page_number = 1
    
    try:
        posts = paginator.page(page_number)
    except:
        posts = paginator.page(1)
    
    # 生成页码范围
    total_pages = paginator.num_pages
    page_numbers = list(range(1, total_pages + 1))
    
    context = {
        'posts': posts,
        'search_query': search_query,
        'page_numbers': page_numbers,
        'current_page': page_number
    }
    
    return render(request, "learn_post/learn_post.html", context)


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from .models import ReservationPost, ReservationOrder
from user_center.models import User
from decimal import Decimal
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone


def reservation(request):
    # 获取搜索参数
    search_query = request.GET.get('search', '')
    
    # 获取所有预约帖子并按创建时间倒序排序
    posts = ReservationPost.objects.all().order_by('-created_time')
    
    # 如果有搜索词，过滤帖子
    if search_query:
        posts = posts.filter(title__icontains=search_query)
    
    # 分页处理
    paginator = Paginator(posts, 10)  # 每页显示10条
    page = request.GET.get('page', 1)
    try:
        page = int(page)
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    
    posts = paginator.get_page(page)
    
    # 生成要显示的页码范围
    page_range = list(paginator.page_range)
    if len(page_range) > 5:
        if page <= 3:
            page_range = page_range[:5]
        elif page >= len(page_range) - 2:
            page_range = page_range[-5:]
        else:
            page_range = page_range[page-3:page+2]
    
    context = {
        'posts': posts,
        'search_query': search_query,
        'page_numbers': page_range,
        'current_page': page,
    }
    
    return render(request, "reservation/reservation.html", context)

def create_reservation_post(request):
    if not request.session.get('is_authenticated'):
        return JsonResponse({'status': 'error', 'message': '请先登录'})
        
    if request.method == 'POST':
        try:
            # 获取当前用户
            user_id = request.session.get('user_id')
            author = User.objects.get(id=user_id)
            
            # 获取表单数据
            title = request.POST.get('title')
            content = request.POST.get('content')
            service_time = request.POST.get('service_time')
            service_duration = request.POST.get('service_duration')
            location = request.POST.get('location')
            max_participants = int(request.POST.get('max_participants', 1))
            price = Decimal(request.POST.get('price', '0.00'))
            wechat = request.POST.get('wechat')
            
            # 创建预约帖子
            post = ReservationPost(
                title=title,
                content=content,
                service_time=service_time,
                service_duration=service_duration,
                location=location,
                max_participants=max_participants,
                price=price,
                wechat=wechat,
                author=author
            )
            
            # 处理封面图片
            if 'cover_image' in request.FILES:
                post.cover_image = request.FILES['cover_image']
            
            # 保存帖子
            post.save()
            
            return JsonResponse({
                'status': 'success',
                'message': '发布成功！',
                'redirect_url': '/square/'  # 发布成功后重定向到广场页面
            })
            
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '用户信息获取失败，请重新登录'
            })
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'输入数据格式错误: {str(e)}'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'发布失败: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': '不支持的请求方法'
    })

def reservation_detail(request, post_id):
    """预约帖子详情页"""
    try:
        post = ReservationPost.objects.get(id=post_id)
        # 检查用户是否已预约
        has_booked = False
        if request.session.get('is_authenticated'):
            user = User.objects.get(id=request.session.get('user_id'))
            has_booked = Reservation.objects.filter(user=user, post=post, status='active').exists()
        
        context = {
            'post': post,
            'has_booked': has_booked,
        }
        return render(request, 'reservation/reservation_detail.html', context)
    except ReservationPost.DoesNotExist:
        messages.error(request, '帖子不存在')
        return redirect('reservation:reservation')

@login_required
def reserve_post(request, post_id):
    """预约服务"""
    post = get_object_or_404(ReservationPost, id=post_id)
    
    # 检查是否已满
    if post.current_participants >= post.max_participants:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': '预约已满'}, status=400)
        return HttpResponseBadRequest('预约已满')
    
    # 创建预约订单
    order = ReservationOrder.objects.create(
        post=post,
        user=request.user,
        price=post.price,
        status='pending'
    )
    
    # 更新预约人数
    post.current_participants += 1
    post.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': '预约成功',
            'redirect_url': f'/reservation/order/{order.id}/'
        })
    return redirect('reservation:order_detail', order_id=order.id)
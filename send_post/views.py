from django.shortcuts import render, redirect
from django.contrib import messages
from square.models import LearnPost
from reservation.models import ReservationPost
from decimal import Decimal
from .forms import StudyMaterialPostForm
from .models import StudyMaterialPost, Purchase, Comment
from django.urls import reverse
from user_center.models import User
from django.http import JsonResponse
import logging
import traceback
from django.utils import timezone
import json

logger = logging.getLogger(__name__)

# Create your views here.
def send_post(request):
    if not request.session.get('is_authenticated'):
        return redirect('/user_center/login/')
    return render(request, 'send_post/send_post.html', {
        'is_authenticated': request.session.get('is_authenticated', False)
    })

def learn_post_view(request):
    """显示学习资料发布页面"""
    if not request.session.get('is_authenticated'):
        return redirect('/user_center/login/')
    form = StudyMaterialPostForm()
    return render(request, 'send_post/learn_post.html', {
        'form': form,
        'is_authenticated': True
    })

def reservation_post_view(request):
    """显示预约服务发布页面"""
    if not request.session.get('is_authenticated'):
        return redirect('/user_center/login/')
    return render(request, 'send_post/reservation.html')

def create_learn_post(request):
    """处理学习资料帖子的创建"""
    if not request.session.get('is_authenticated'):
        messages.error(request, '请先登录后再发布学习资料')
        return redirect('/user_center/login/')
        
    if request.method == 'POST':
        try:
            # 检查用户ID是否存在于session中
            user_id = request.session.get('user_id')
            if not user_id:
                logger.error('No user_id in session')
                messages.error(request, '用户信息不完整，请重新登录')
                return redirect('/user_center/login/')

            # 尝试获取用户对象
            try:
                user = User.objects.get(id=user_id)
                logger.info(f'Found user: {user.username} (ID: {user.id})')
            except User.DoesNotExist:
                logger.error(f'User with ID {user_id} does not exist')
                messages.error(request, '用户不存在，请重新登录')
                return redirect('/user_center/login/')

            # 处理表单
            form = StudyMaterialPostForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    post = form.save(commit=False)
                    post.author = user
                    logger.info(f'Saving post with author: {user.username} (ID: {user.id})')
                    post.save()
                    messages.success(request, '学习资料发布成功！')
                    return redirect('square:index')
                except Exception as e:
                    logger.error(f'Error saving post: {str(e)}\n{traceback.format_exc()}')
                    messages.error(request, f'保存帖子时出错：{str(e)}')
                    return render(request, 'send_post/learn_post.html', {
                        'form': form,
                        'is_authenticated': True
                    })
            else:
                logger.error(f'Form validation failed: {form.errors}')
                return render(request, 'send_post/learn_post.html', {
                    'form': form,
                    'is_authenticated': True
                })
        except Exception as e:
            logger.error(f'Unexpected error: {str(e)}\n{traceback.format_exc()}')
            messages.error(request, f'发布失败：{str(e)}')
            return render(request, 'send_post/learn_post.html', {
                'form': StudyMaterialPostForm(request.POST, request.FILES),
                'is_authenticated': True
            })
    return redirect('send_post:learn_post')

def create_reservation_post(request):
    """处理预约服务帖子的创建"""
    if not request.session.get('is_authenticated'):
        return JsonResponse({
            'status': 'error',
            'message': '请先登录后再发布预约信息',
            'redirect_url': '/user_center/login/'
        })
        
    if request.method == 'POST':
        try:
            user = User.objects.get(id=request.session['user_id'])
            post = ReservationPost(
                title=request.POST['title'],
                content=request.POST['content'],
                price=Decimal(request.POST['price']),
                author=user,
                service_time=request.POST['service_time'],
                location=request.POST['location'],
                max_participants=int(request.POST['max_participants']),
                service_duration=request.POST['service_duration'],
                wechat=request.POST['wechat']
            )
            
            # 处理封面图片
            if 'cover_image' in request.FILES:
                post.cover_image = request.FILES['cover_image']
            
            post.save()
            return JsonResponse({
                'status': 'success',
                'message': '预约服务发布成功！',
                'redirect_url': reverse('square:index')
            })
        except Exception as e:
            logger.error(f'发布预约服务失败: {str(e)}\n{traceback.format_exc()}')
            return JsonResponse({
                'status': 'error',
                'message': f'发布失败：{str(e)}',
                'redirect_url': None
            })
    return JsonResponse({
        'status': 'error',
        'message': '无效的请求方法',
        'redirect_url': None
    })

def create_study_material(request):
    if not request.session.get('is_authenticated'):
        return redirect('/user_center/login/')
        
    if request.method == 'POST':
        form = StudyMaterialPostForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.get(id=request.session['user_id'])
            post = form.save(commit=False)
            post.author = user
            post.save()
            messages.success(request, '学习资料发布成功！')
            return redirect('square:post_detail', post_type='studymaterialpost', post_id=post.id)
        else:
            # 如果表单验证失败，返回表单并显示错误信息
            return render(request, 'send_post/learn_post.html', {
                'form': form,
                'title': '发布学习资料'
            })
    else:
        # GET 请求时显示空表单
        form = StudyMaterialPostForm()
        return render(request, 'send_post/learn_post.html', {
            'form': form,
            'title': '发布学习资料'
        })

def learn_post_detail(request, post_id):
    """学习资料帖子详情页"""
    try:
        post = StudyMaterialPost.objects.get(id=post_id)
        # 检查用户是否已购买
        has_purchased = False
        if request.session.get('is_authenticated'):
            user = User.objects.get(id=request.session.get('user_id'))
            has_purchased = Purchase.objects.filter(buyer=user, post=post).exists()
        
        # 获取评论列表
        comments = post.post_comments.all()
        
        context = {
            'post': post,
            'has_purchased': has_purchased,
            'comments': comments,
        }
        return render(request, 'send_post/learn_post_detail.html', context)
    except StudyMaterialPost.DoesNotExist:
        messages.error(request, '帖子不存在')
        return redirect('send_post:learn_post')

def add_comment(request, post_id):
    """添加评论"""
    if not request.session.get('is_authenticated'):
        return JsonResponse({
            'status': 'error',
            'message': '请先登录后再发表评论'
        })
    
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': '无效的请求方法'
        })
    
    try:
        # 获取帖子和用户
        post = StudyMaterialPost.objects.get(id=post_id)
        user = User.objects.get(id=request.session.get('user_id'))
        
        # 检查用户是否已购买
        if not Purchase.objects.filter(buyer=user, post=post).exists():
            return JsonResponse({
                'status': 'error',
                'message': '只有购买后才能发表评论'
            })
        
        # 获取评论内容
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({
                'status': 'error',
                'message': '评论内容不能为空'
            })
        
        # 创建评论
        comment = Comment.objects.create(
            post=post,
            user=user,
            content=content
        )
        
        # 返回评论信息
        return JsonResponse({
            'status': 'success',
            'message': '评论发表成功',
            'comment': {
                'username': user.username,
                'content': comment.content,
                'created_time': comment.created_time.strftime('%Y-%m-%d %H:%M')
            }
        })
        
    except StudyMaterialPost.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '帖子不存在'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '用户不存在'
        })
    except Exception as e:
        logger.error(f'添加评论失败: {str(e)}\n{traceback.format_exc()}')
        return JsonResponse({
            'status': 'error',
            'message': f'评论发表失败：{str(e)}'
        })

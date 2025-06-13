from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404, HttpResponse
from reservation.models import ReservationPost, ReservationOrder, Reservation
from send_post.models import StudyMaterialPost, Purchase
from django.core.paginator import Paginator
from itertools import chain
from operator import attrgetter
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib import messages
from django.db.models import F
from django.db import transaction
from user_center.models import User
from django.contrib.contenttypes.models import ContentType
from comments.models import StudyMaterialComment
import json
import logging
import traceback
from reservation.utils import send_reservation_notification

logger = logging.getLogger(__name__)

# Create your views here.
def square(request):
    # 获取搜索关键词
    search_query = request.GET.get('search', '')
    
    # 获取最新的预约帖子
    reservation_posts = ReservationPost.objects.all()
    # 获取最新的学习资料帖子
    study_posts = StudyMaterialPost.objects.all()
    
    # 如果有搜索关键词，过滤标题
    if search_query:
        reservation_posts = reservation_posts.filter(title__icontains=search_query)
        study_posts = study_posts.filter(title__icontains=search_query)
    
    # 按创建时间排序
    reservation_posts = reservation_posts.order_by('-created_time')
    study_posts = study_posts.order_by('-created_time')
    
    # 合并两种帖子并按创建时间排序
    all_posts = sorted(
        chain(reservation_posts, study_posts),
        key=attrgetter('created_time'),
        reverse=True
    )
    
    # 分页处理
    paginator = Paginator(all_posts, 10)  # 每页显示10条
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
    
    return render(request, 'square/square.html', context)

def post_detail(request, post_type, post_id):
    try:
        if post_type == 'reservationpost':
            post = get_object_or_404(ReservationPost, id=post_id)
            has_reserved = False
            if request.user.is_authenticated:
                # 检查用户是否已预约
                has_reserved = post.reservations.filter(user=request.user, status='active').exists()
            context = {
                'post': post,
                'post_type': 'reservation',
                'has_reserved': has_reserved
            }
            return render(request, 'square/post_detail.html', context)
        elif post_type == 'studymaterialpost':
            post = get_object_or_404(StudyMaterialPost, id=post_id)
            has_purchased = False
            if request.user.is_authenticated:
                has_purchased = Purchase.objects.filter(
                    buyer=request.user,
                    post=post
                ).exists()
            
            # 获取评论列表
            try:
                comments = StudyMaterialComment.objects.filter(
                    post=post
                ).select_related('user').order_by('-created_time')
            except:
                # If the comments table doesn't exist yet, just use an empty list
                comments = []
            
            context = {
                'post': post,
                'post_type': 'study',
                'has_purchased': has_purchased,
                'comments': comments
            }
            return render(request, 'square/study_detail.html', context)
        else:
            raise Http404("Invalid post type")
    except Http404:
        return redirect('square:index')

@login_required
@require_POST
def purchase_study_material(request, post_id):
    post = get_object_or_404(StudyMaterialPost, id=post_id)
    
    # 检查是否已购买
    if Purchase.objects.filter(buyer=request.user, post=post).exists():
        return JsonResponse({
            'status': 'error',
            'message': '您已经购买过这份资料'
        })
    
    # 创建购买记录
    Purchase.objects.create(
        buyer=request.user,
        seller=post.author,
        post=post,
        post_title=post.title,
        price=post.price
    )
    
    return JsonResponse({
        'status': 'success',
        'message': '购买成功！',
        'redirect_url': reverse('square:post_detail', kwargs={
            'post_type': 'studymaterialpost',
            'post_id': post_id
        })
    })

@login_required
def download_file(request, post_id):
    post = get_object_or_404(StudyMaterialPost, id=post_id)
    
    # 检查是否已购买
    if not Purchase.objects.filter(buyer=request.user, post=post).exists():
        return JsonResponse({
            'status': 'error',
            'message': '请先购买资料'
        })
    
    if not post.file:
        return JsonResponse({
            'status': 'error',
            'message': '文件不存在'
        })
    
    try:
        response = HttpResponse(post.file, content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename="{post.file.name.split("/")[-1]}"'
        return response
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': '下载失败，请稍后重试'
        })

def check_login(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_authenticated'):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': '请先登录后再进行操作',
                    'redirect_url': '/user_center/login/'
                })
            return redirect('/user_center/login/')
        return view_func(request, *args, **kwargs)
    return wrapper

@check_login
@require_POST
def reserve_post(request, post_id):
    """处理预约请求"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            with transaction.atomic():
                logger.info(f"开始处理预约请求 - 用户ID: {request.session.get('user_id')}, 帖子ID: {post_id}")
                
                # 获取用户对象
                try:
                    user = User.objects.get(id=request.session.get('user_id'))
                except User.DoesNotExist:
                    logger.error("用户不存在")
                    return JsonResponse({
                        'status': 'error',
                        'message': '用户信息获取失败，请重新登录'
                    })
                
                # 使用 select_for_update 来锁定记录，防止并发问题
                post = ReservationPost.objects.select_for_update().get(id=post_id)
                logger.info(f"找到预约帖子 - 标题: {post.title}, 状态: {post.status}")
                
                # 检查帖子状态
                if post.status != 'open':
                    logger.warning(f"帖子状态不是开放 - 当前状态: {post.status}")
                    return JsonResponse({
                        'status': 'error',
                        'message': '该预约已关闭或已满员'
                    })
                
                # 检查是否已预约
                existing_reservation = post.reservations.filter(user=user, status='active').exists()
                if existing_reservation:
                    logger.warning(f"用户已经预约过 - 用户ID: {user.id}, 帖子ID: {post_id}")
                    return JsonResponse({
                        'status': 'error',
                        'message': '您已经预约过了'
                    })
                
                # 检查是否还有剩余名额
                if post.current_participants >= post.max_participants:
                    logger.warning("预约人数已满")
                    post.status = 'full'
                    post.save()
                    return JsonResponse({
                        'status': 'error',
                        'message': '预约名额已满'
                    })
                
                # 增加当前预约人数
                logger.info(f"当前预约人数: {post.current_participants}, 最大人数: {post.max_participants}")
                post.current_participants += 1
                
                # 检查是否达到人数限制
                if post.current_participants >= post.max_participants:
                    post.status = 'full'
                
                # 创建预约记录
                reservation = Reservation.objects.create(
                    post=post,
                    user=user,
                    status='active'
                )
                logger.info(f"创建预约记录成功 - ID: {reservation.id}")
                
                # 创建预约订单
                order = ReservationOrder.objects.create(
                    post=post,
                    user=user,
                    price=post.price,
                    status='pending'  # 创建待支付订单
                )
                logger.info(f"创建预约订单成功 - 订单号: {order.order_number}")
                
                # 保存帖子状态
                post.save()
                logger.info(f"更新后预约人数: {post.current_participants}")
                
                # 发送邮件通知
                try:
                    send_reservation_notification(reservation)
                    logger.info(f"发送预约通知邮件成功 - 发送给: {post.author.email}")
                except Exception as e:
                    logger.error(f"发送预约通知邮件失败: {str(e)}")
                    # 不影响预约流程，继续执行
                
                logger.info("预约流程完成")
                return JsonResponse({
                    'status': 'success',
                    'message': '预约成功！',
                    'order_number': order.order_number,
                    'post_status': post.status,
                    'current_participants': post.current_participants,
                    'wechat': post.wechat
                })
                
        except ReservationPost.DoesNotExist:
            logger.error(f"预约帖子不存在 - ID: {post_id}")
            return JsonResponse({
                'status': 'error',
                'message': '预约帖子不存在'
            })
        except Exception as e:
            logger.error(f"预约过程中发生错误: {str(e)}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': f'预约失败：{str(e)}'
            })
    else:
        # 非AJAX请求的处理
        try:
            with transaction.atomic():
                # 获取用户对象
                try:
                    user = User.objects.get(id=request.session.get('user_id'))
                except User.DoesNotExist:
                    messages.error(request, '用户信息获取失败，请重新登录')
                    return redirect('/user_center/login/')
                
                # 使用 select_for_update 来锁定记录，防止并发问题
                post = ReservationPost.objects.select_for_update().get(id=post_id)
                
                if post.status != 'open':
                    messages.error(request, '该预约已关闭或已满员')
                    return redirect('square:post_detail', post_type='reservationpost', post_id=post_id)
                
                if post.reservations.filter(user=user, status='active').exists():
                    messages.error(request, '您已经预约过了')
                    return redirect('square:post_detail', post_type='reservationpost', post_id=post_id)
                
                # 检查是否还有剩余名额
                if post.current_participants >= post.max_participants:
                    messages.error(request, '预约名额已满')
                    return redirect('square:post_detail', post_type='reservationpost', post_id=post_id)
                
                # 增加当前预约人数
                post.current_participants += 1
                
                # 检查是否达到人数限制
                if post.current_participants >= post.max_participants:
                    post.status = 'full'
                
                # 创建预约记录
                reservation = Reservation.objects.create(
                    post=post,
                    user=user,
                    status='active'
                )
                
                # 创建预约订单
                order = ReservationOrder.objects.create(
                    post=post,
                    user=user,
                    price=post.price,
                    status='pending'
                )
                
                # 保存帖子状态
                post.save()
                
                # 发送邮件通知
                try:
                    send_reservation_notification(reservation)
                    logger.info(f"发送预约通知邮件成功 - 发送给: {post.author.email}")
                except Exception as e:
                    logger.error(f"发送预约通知邮件失败: {str(e)}")
                    # 不影响预约流程，继续执行
                
                messages.success(request, '预约成功！')
                
        except ReservationPost.DoesNotExist:
            messages.error(request, '预约帖子不存在')
            return redirect('square:index')
        except Exception as e:
            logger.error(f"非AJAX预约过程中发生错误: {str(e)}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            messages.error(request, f'预约失败：{str(e)}')
            
        return redirect('square:post_detail', post_type='reservationpost', post_id=post_id)

@login_required
@require_POST
def post_comment(request, post_id):
    """处理评论提交"""
    try:
        # 获取帖子
        post = get_object_or_404(StudyMaterialPost, id=post_id)
        
        # 检查是否已购买
        if not Purchase.objects.filter(buyer=request.user, post=post).exists():
            return JsonResponse({
                'status': 'error',
                'message': '请先购买资料后再评论'
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
        StudyMaterialComment.objects.create(
            post=post,
            user=request.user,
            content=content
        )
        
        return JsonResponse({
            'status': 'success',
            'message': '评论发表成功'
        })
        
    except StudyMaterialPost.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '帖子不存在'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': '无效的请求数据'
        })
    except Exception as e:
        logger.error(f"评论发表失败: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': '评论发表失败，请稍后重试'
        })

@login_required
@require_POST
def delete_post(request, post_type, post_id):
    """删除帖子"""
    try:
        if post_type == 'studymaterialpost':
            post = get_object_or_404(StudyMaterialPost, id=post_id)
        elif post_type == 'reservationpost':
            post = get_object_or_404(ReservationPost, id=post_id)
        else:
            return JsonResponse({
                'status': 'error',
                'message': '无效的帖子类型'
            })
        
        # 检查是否是帖子作者
        if post.author != request.user:
            return JsonResponse({
                'status': 'error',
                'message': '您没有权限删除这个帖子'
            })
        
        # 删除帖子
        post.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': '帖子已成功删除'
        })
        
    except Exception as e:
        logger.error(f"删除帖子时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            'status': 'error',
            'message': '删除失败，请稍后重试'
        })

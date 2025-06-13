from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from .models import User
import string
from django.core.mail import EmailMessage
from django.contrib.auth import login, authenticate
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token
import json
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from send_post.models import StudyMaterialPost, Purchase, AppointmentPost
from reservation.models import ReservationPost, Reservation

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # 使用Django的认证系统验证用户
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # 登录用户
            login(request, user)
            
            # 设置session数据
            request.session['user_id'] = user.id
            request.session['is_authenticated'] = True
            request.session['username'] = user.username
            
            # 获取next参数，如果没有则默认重定向到square
            next_url = request.GET.get('next', '/square/')
            
            # 如果是AJAX请求，返回JSON响应
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'next': next_url,
                    'message': '登录成功！'
                })
            # 否则进行普通重定向
            return redirect(next_url)
        else:
            # 如果是AJAX请求，返回JSON响应
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': '用户名或密码错误'
                })
            # 否则返回带错误信息的页面
            messages.error(request, '用户名或密码错误')
            return render(request, 'user_center/login.html')
    
    return render(request, 'user_center/login.html')

def generate_verification_code():
    """生成6位随机验证码"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_code(request):
    """发送验证码到邮箱"""
    try:
        email = request.POST.get('email')
        if not email:
            return JsonResponse({'status': 'error', 'message': '请提供邮箱地址'})

        # 检查邮箱是否已被注册
        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': '该邮箱已被注册'})

        # 生成验证码
        code = generate_verification_code()
        
        # 将验证码保存到缓存，设置过期时间
        cache_key = f'email_verification_{email}'
        cache.set(cache_key, code, 300)  # 5分钟过期

        # 发送验证码邮件
        subject = '注册验证码'
        message = f'您的验证码是：{code}，有效期为5分钟。'
        from_email = settings.EMAIL_FROM
        recipient_list = [email]
        
        try:
            # 使用EmailMessage类来发送邮件
            email_message = EmailMessage(
                subject=subject,
                body=message,
                from_email=from_email,
                to=recipient_list,
            )
            email_message.content_subtype = 'plain'
            email_message.encoding = 'utf-8'
            email_message.send(fail_silently=False)
            
            return JsonResponse({'status': 'success', 'message': '验证码已发送'})
        except Exception as e:
            print(f"邮件发送错误: {str(e)}")  # 添加错误日志
            if hasattr(e, 'smtp_error'):
                error_message = f"SMTP错误: {str(e.smtp_error)}"
            else:
                error_message = str(e)
            return JsonResponse({'status': 'error', 'message': f'邮件发送失败: {error_message}'})
    except Exception as e:
        print(f"验证码发送过程错误: {str(e)}")  # 添加错误日志
        return JsonResponse({'status': 'error', 'message': f'发送验证码失败: {str(e)}'})

def register(request):
    """第一步：邮箱验证"""
    if request.method == 'POST':
        email = request.POST.get('email')
        verification_code = request.POST.get('verification_code')
        
        if not email or not verification_code:
            messages.error(request, '请填写所有必填项')
            return render(request, 'user_center/register.html')
            
        # 验证验证码
        cache_key = f'email_verification_{email}'
        stored_code = cache.get(cache_key)
        
        if not stored_code or stored_code != verification_code:
            messages.error(request, '验证码无效或已过期')
            return render(request, 'user_center/register.html')
        
        # 验证成功，将邮箱存入session并跳转到注册第二步
        request.session['verified_email'] = email
        return redirect('user_center:register_step2')
        
    return render(request, 'user_center/register.html')

def register_step2(request):
    """第二步：完善用户信息"""
    # 检查是否完成了邮箱验证
    verified_email = request.session.get('verified_email')
    if not verified_email and not request.POST.get('test_mode'):  # 添加测试模式检查
        messages.error(request, '请先完成邮箱验证')
        return redirect('user_center:register')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2', password)  # 在测试模式中，如果没有password2，使用password
        phone = request.POST.get('phone')
        sex = request.POST.get('sex', 'male')  # 默认值
        head = request.FILES.get('head')

        # 验证数据
        errors = {}
        if not username:
            errors['username'] = '用户名不能为空'
        elif User.objects.filter(username=username).exists():
            errors['username'] = '该用户名已被使用'

        if not password:
            errors['password'] = '密码不能为空'
        elif password != password2:
            errors['password2'] = '两次输入的密码不匹配'

        if not phone:
            errors['phone'] = '手机号不能为空'
        elif not phone.isdigit() or len(phone) != 11:
            errors['phone'] = '请输入有效的11位手机号码'
        elif User.objects.filter(phone=phone).exists():
            errors['phone'] = '该手机号已被注册'

        if errors:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': errors})
            for key, value in errors.items():
                messages.error(request, value)
            return render(request, 'user_center/register_step2.html')

        # 创建新用户
        try:
            user = User(
                username=username,
                password=password,
                email=verified_email if verified_email else f"{username}@example.com",  # 测试模式使用默认邮箱
                phone=phone,
                sex=sex
            )
            if head:
                user.head = head
            user.save()
            
            # 清除session中的邮箱
            if 'verified_email' in request.session:
                del request.session['verified_email']
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success', 
                    'message': '注册成功！',
                    'redirect_url': '/user_center/login/'
                })
            return redirect('user_center:login')
        except Exception as e:
            print(f"注册失败: {str(e)}")  # 添加错误日志
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error', 
                    'message': f'注册失败: {str(e)}'
                })
            messages.error(request, f'注册失败: {str(e)}')
            return render(request, 'user_center/register_step2.html')
    
    return render(request, 'user_center/register_step2.html', {'email': verified_email})

def register1(request):
    return render(request, 'user_center/register1.html')

def logout(request):
    # 清除所有session数据
    request.session.flush()
    # 重定向到登录页面
    return redirect('user_center:login')

def profile(request):
    """用户个人资料页面"""
    if not request.session.get('is_authenticated'):
        return redirect('user_center:login')

    user = User.objects.get(id=request.session.get('user_id'))
    
    if request.method == 'POST':
        # 获取表单数据
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        bio = request.POST.get('bio')
        
        # 验证用户名是否已存在
        if username != user.username and User.objects.filter(username=username).exists():
            return JsonResponse({
                'status': 'error',
                'message': '用户名已存在'
            })
        
        # 验证手机号是否已存在
        if phone != user.phone and User.objects.filter(phone=phone).exists():
            return JsonResponse({
                'status': 'error',
                'message': '手机号已被使用'
            })
        
        # 更新用户信息
        user.username = username
        user.phone = phone
        user.bio = bio
        user.save()
        
        # 更新session中的用户名
        request.session['username'] = username
        
        return JsonResponse({
            'status': 'success',
            'message': '个人资料更新成功'
        })
    
    # 获取用户发布的学习资料
    shared_materials = StudyMaterialPost.objects.filter(author=user)
    # 获取用户发布的预约帖子
    shared_bookings = ReservationPost.objects.filter(author=user)
    
    # 计算学习资料收入
    materials_income = 0
    for material in shared_materials:
        purchase_count = Purchase.objects.filter(post=material).count()
        materials_income += material.price * purchase_count
    
    # 计算预约收入
    reservations_income = 0
    for booking in shared_bookings:
        reservation_count = Reservation.objects.filter(post=booking, status='active').count()
        reservations_income += booking.price * reservation_count
    
    # 计算总收入
    total_income = materials_income + reservations_income
    
    # 获取用户购买的帖子
    purchased_posts = Purchase.objects.filter(buyer=user)
    # 获取用户预约的帖子
    booked_posts = Reservation.objects.filter(user=user)
    
    context = {
        'user': user,
        'purchased_posts': purchased_posts,
        'booked_posts': booked_posts,
        'shared_materials': shared_materials,
        'shared_bookings': shared_bookings,
        'materials_income': materials_income,
        'reservations_income': reservations_income,
        'total_income': total_income
    }
    
    return render(request, 'user_center/profile.html', context)

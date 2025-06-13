from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_reservation_notification(reservation):
    """
    Send email notification to the post author when a new reservation is made
    """
    subject = f'新预约通知 - {reservation.post.title}'
    
    # 准备邮件内容的上下文
    context = {
        'post_title': reservation.post.title,
        'user_name': reservation.user.username,
        'reservation_time': reservation.created_time.strftime('%Y-%m-%d %H:%M:%S'),
        'service_time': reservation.post.service_time,
        'service_duration': reservation.post.service_duration,
        'location': reservation.post.location,
    }
    
    # 使用HTML模板渲染邮件内容
    html_message = render_to_string('reservation/email/reservation_notification.html', context)
    
    # 纯文本版本的邮件内容
    plain_message = f"""
    您好！

    您发布的预约服务"{reservation.post.title}"收到了新的预约：

    预约用户：{reservation.user.username}
    预约时间：{reservation.created_time.strftime('%Y-%m-%d %H:%M:%S')}
    服务时间：{reservation.post.service_time}
    服务时长：{reservation.post.service_duration}
    服务地点：{reservation.post.location}

    请及时查看并处理！
    """
    
    # 发送邮件
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reservation.post.author.email],
        html_message=html_message,
        fail_silently=False,
    ) 
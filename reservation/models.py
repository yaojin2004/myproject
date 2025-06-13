from django.db import models
from django.utils import timezone
from django.conf import settings

class ReservationPost(models.Model):
    '''预约帖子表'''
    title = models.CharField('标题', max_length=128)
    content = models.TextField('服务描述')
    service_time = models.CharField('服务时间', max_length=128)
    service_duration = models.CharField('服务时长', max_length=64)
    location = models.CharField('服务地点', max_length=256)
    max_participants = models.IntegerField('最大预约人数', default=1)
    current_participants = models.IntegerField('当前预约人数', default=0)
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    wechat = models.CharField('微信联系方式', max_length=64)
    cover_image = models.ImageField('封面图片', upload_to='reservation_covers/', blank=True, null=True, help_text='建议上传一张服务相关的封面图片')
    status = models.CharField('状态', max_length=32, choices=(
        ('open', '开放中'),
        ('full', '已满'),
        ('closed', '已关闭'),
    ), default='open')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservation_posts', verbose_name='作者')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_time']
        verbose_name = '预约帖子'
        verbose_name_plural = '预约帖子'

    def save(self, *args, **kwargs):
        # 检查是否需要更新状态
        if self.current_participants >= self.max_participants:
            self.status = 'full'
        super().save(*args, **kwargs)

class ReservationOrder(models.Model):
    '''预约订单表'''
    post = models.ForeignKey(ReservationPost, on_delete=models.CASCADE, related_name='orders', verbose_name='预约帖子')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservation_orders', verbose_name='预约用户')
    order_number = models.CharField('订单编号', max_length=32, unique=True)
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    status = models.CharField('状态', max_length=32, choices=(
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('cancelled', '已取消'),
        ('completed', '已完成'),
    ), default='pending')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['-created_time']
        verbose_name = '预约订单'
        verbose_name_plural = '预约订单'

    def __str__(self):
        return f"{self.order_number} - {self.user.username} 预约 {self.post.title}"

    def save(self, *args, **kwargs):
        # 生成订单编号
        if not self.order_number:
            self.order_number = f"R{timezone.now().strftime('%Y%m%d%H%M%S')}{self.user.id}"
        super().save(*args, **kwargs)

class Reservation(models.Model):
    '''预约记录表'''
    post = models.ForeignKey(ReservationPost, on_delete=models.CASCADE, related_name='reservations', verbose_name='预约帖子')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_reservations', verbose_name='预约用户')
    created_time = models.DateTimeField('预约时间', auto_now_add=True)
    status = models.CharField('状态', max_length=32, choices=(
        ('active', '有效'),
        ('cancelled', '已取消'),
    ), default='active')

    class Meta:
        ordering = ['-created_time']
        verbose_name = '预约记录'
        verbose_name_plural = '预约记录'
        # 确保同一用户不能重复预约同一个帖子
        unique_together = ['post', 'user']

    def __str__(self):
        return f"{self.user.username} 预约了 {self.post.title}"

class Comment(models.Model):
    '''评论表'''
    post = models.ForeignKey(ReservationPost, on_delete=models.CASCADE, related_name='comments', verbose_name='预约帖子')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservation_comments', verbose_name='评论用户')
    content = models.TextField('评论内容')
    created_time = models.DateTimeField('评论时间', auto_now_add=True)

    class Meta:
        ordering = ['-created_time']
        verbose_name = '评论'
        verbose_name_plural = '评论'

    def __str__(self):
        return f"{self.user.username}对{self.post.title}的评论"

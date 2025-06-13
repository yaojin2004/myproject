from django.db import models
from user_center.models import User
from django.utils import timezone
from decimal import Decimal

# Create your models here.
# 这里是发布帖子的表结构（分为两类：预约类、学习资料类）

class AppointmentPost(models.Model):
    '''预约帖子表'''
    id = models.AutoField(primary_key=True, verbose_name='帖子ID')
    title = models.CharField('标题', max_length=128)
    content = models.TextField('内容')
    price = models.DecimalField('价格', max_digits=10, decimal_places=2, help_text='请输入服务价格')
    location = models.CharField('地点', max_length=256)
    appointment_time = models.DateTimeField('预约时间')
    people_limit = models.IntegerField('人数限制', default=1)
    current_people = models.IntegerField('当前人数', default=0)
    wechat = models.CharField('微信号', max_length=64)
    image = models.ImageField('帖子图片', upload_to='appointment_posts/', blank=True, null=True, help_text='建议上传一张与预约内容相关的图片')
    status = models.CharField('状态', max_length=32, choices=(
        ('open', '开放中'),
        ('full', '已满'),
        ('closed', '已关闭'),
    ), default='open')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_time']
        verbose_name = '预约帖子'
        verbose_name_plural = '预约帖子'

class StudyMaterialPost(models.Model):
    '''学习资料帖子表'''
    id = models.AutoField(primary_key=True, verbose_name='帖子ID')
    title = models.CharField('标题', max_length=128)
    content = models.TextField('内容')
    subject = models.CharField('科目', max_length=64, choices=(
        ('math', '数学'),
        ('chinese', '语文'),
        ('english', '英语'),
        ('physics', '物理'),
        ('chemistry', '化学'),
        ('biology', '生物'),
        ('history', '历史'),
        ('geography', '地理'),
        ('politics', '政治'),
        ('other', '其他'),
    ))
    material_type = models.CharField('资料类型', max_length=32, choices=(
        ('document', '文档'),
        ('video', '视频'),
        ('link', '链接'),
        ('other', '其他'),
    ))
    price = models.DecimalField('价格', max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text='请输入资料价格')
    image = models.ImageField('封面图片', upload_to='study_materials/images/', blank=True, null=True, help_text='建议上传一张资料相关的封面图片')
    file = models.FileField('附件', upload_to='study_materials/', blank=True, null=True)
    file_url = models.URLField('资料链接', max_length=500, blank=True, null=True, help_text='请输入资料的网络链接')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_time']
        verbose_name = '学习资料'
        verbose_name_plural = '学习资料'

class Purchase(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    post = models.ForeignKey(StudyMaterialPost, on_delete=models.CASCADE, related_name='purchases')
    post_title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_time = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-purchase_time']

    def __str__(self):
        return f"{self.buyer.username} purchased {self.post_title} from {self.seller.username}"

class Comment(models.Model):
    """评论表"""
    post = models.ForeignKey(StudyMaterialPost, on_delete=models.CASCADE, related_name='post_comments', verbose_name='帖子')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments', verbose_name='评论者')
    content = models.TextField('评论内容')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['-created_time']
        verbose_name = '评论'
        verbose_name_plural = '评论'

    def __str__(self):
        return f"{self.user.username}'s comment on {self.post.title}"


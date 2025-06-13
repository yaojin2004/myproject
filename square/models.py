from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from send_post.models import StudyMaterialPost
from django.conf import settings

class BasePost(models.Model):
    """帖子基类，包含共同字段"""
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='作者')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    views = models.PositiveIntegerField(default=0, verbose_name='浏览量')
    likes = models.PositiveIntegerField(default=0, verbose_name='点赞数')

    class Meta:
        abstract = True
        ordering = ['-created_at']

class LearnPost(BasePost):
    """学习资料帖子"""
    file_link = models.URLField(verbose_name='资料链接')
    subject_area = models.CharField(max_length=50, verbose_name='学科领域')
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', '入门'),
        ('intermediate', '进阶'),
        ('advanced', '高级')
    ], verbose_name='难度等级')

    class Meta:
        verbose_name = '学习资料'
        verbose_name_plural = '学习资料'

    def __str__(self):
        return f'学习资料: {self.title}'


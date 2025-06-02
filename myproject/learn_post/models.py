from django.db import models
from user_center.models import User
# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)  # 帖子标题
    description = models.TextField(blank=True, null=True)  # 帖子简介
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)  # 帖子作者
    file_link = models.URLField(blank=True, null=True)  # 文件链接
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)  # 图片

    def __str__(self):
        return self.title
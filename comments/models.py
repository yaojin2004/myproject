from django.db import models
from django.utils import timezone
from send_post.models import StudyMaterialPost
from user_center.models import User

class StudyMaterialComment(models.Model):
    """学习资料评论表"""
    post = models.ForeignKey(StudyMaterialPost, on_delete=models.CASCADE, related_name='comments', verbose_name='学习资料')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_comments', verbose_name='评论者')
    content = models.TextField(verbose_name='评论内容')
    created_time = models.DateTimeField(default=timezone.now, verbose_name='评论时间')

    class Meta:
        verbose_name = '学习资料评论'
        verbose_name_plural = '学习资料评论'
        ordering = ['-created_time']

    def __str__(self):
        return f'{self.user.username}对{self.post.title}的评论'

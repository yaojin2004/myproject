from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password

# Create your models here.
class User(AbstractUser):
    '''  用户表  '''

    gender = (
        ('male', '男'),
        ('female', '女'),
    )

    phone = models.CharField('手机号', max_length=11, blank=True, null=True)
    head = models.ImageField('头像', upload_to='images', default='/media/images/光遇背景.jpg', blank=True, null=True)
    sex = models.CharField('性别', max_length=32, choices=gender, default='男')
    bio = models.TextField('个人简介', max_length=500, blank=True, null=True)
    created_time = models.DateTimeField('注册时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    def save(self, *args, **kwargs):
        if self._state.adding or (
            not self._state.adding and 
            self.password and 
            not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2'))
        ):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['created_time']
        verbose_name = '用户'
        verbose_name_plural = '用户'
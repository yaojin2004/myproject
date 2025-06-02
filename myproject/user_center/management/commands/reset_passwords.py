from django.core.management.base import BaseCommand
from user_center.models import User
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = '为所有现有用户重置密码为其用户名'

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            # 将密码设置为用户名（临时解决方案）
            user.password = make_password(user.username)
            user.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(f'Successfully reset password for user {user.username}')) 
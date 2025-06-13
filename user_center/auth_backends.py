from django.contrib.auth.backends import BaseBackend
from .models import User

class CustomUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            if user.password == password:  # 注意：实际应用中应该使用加密密码
                return user
        except User.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None 
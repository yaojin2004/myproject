from django.test import TestCase, Client
from django.urls import reverse
from .models import User

# Create your tests here.

class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            phone='13800138000'
        )
        self.login_url = reverse('user_center:login')
        self.register_url = reverse('user_center:register')

    def test_user_login(self):
        """测试用户登录功能"""
        # 测试正确的用户名和密码
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # 应该重定向到首页

        # 测试错误的密码
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # 应该留在登录页面

    def test_user_registration(self):
        """测试用户注册功能"""
        # 测试有效的注册数据
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'phone': '13900139000'
        })
        self.assertEqual(response.status_code, 302)  # 应该重定向到登录页面
        self.assertTrue(User.objects.filter(username='newuser').exists())

        # 测试重复的用户名
        response = self.client.post(self.register_url, {
            'username': 'testuser',  # 已存在的用户名
            'password1': 'anotherpass123',
            'password2': 'anotherpass123',
            'phone': '13700137000'
        })
        self.assertEqual(response.status_code, 200)  # 应该留在注册页面

    def test_user_logout(self):
        """测试用户登出功能"""
        # 先登录
        self.client.login(username='testuser', password='testpass123')
        # 测试登出
        response = self.client.get(reverse('user_center:logout'))
        self.assertEqual(response.status_code, 302)  # 应该重定向到登录页面

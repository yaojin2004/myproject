from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from user_center.models import User
from .models import StudyMaterialPost
from decimal import Decimal

# Create your tests here.

class StudyMaterialTests(TestCase):
    def setUp(self):
        self.client = Client()
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            phone='13800138000'
        )
        # 创建测试资料
        self.study_material = StudyMaterialPost.objects.create(
            title='Test Material',
            content='Test Content',
            price=Decimal('9.99'),
            author=self.user,
            subject='math',
            material_type='document',
            file_url='http://example.com/test.pdf'
        )
        self.create_url = reverse('send_post:learn_post')
        self.detail_url = reverse('send_post:learn_post_detail', 
                                kwargs={'post_id': self.study_material.id})

    def test_create_study_material(self):
        """测试创建学习资料"""
        self.client.login(username='testuser', password='testpass123')
        
        # 创建测试文件
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        response = self.client.post(self.create_url, {
            'title': 'New Material',
            'content': 'New Content',
            'price': '19.99',
            'subject': 'math',
            'material_type': 'document',
            'file_url': 'http://example.com/new.pdf'
        })
        
        self.assertEqual(response.status_code, 302)  # 应该重定向到详情页
        self.assertTrue(StudyMaterialPost.objects.filter(title='New Material').exists())

    def test_view_study_material(self):
        """测试查看学习资料"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Material')

    def test_unauthorized_access(self):
        """测试未授权访问"""
        # 未登录用户尝试创建资料
        response = self.client.post(self.create_url, {
            'title': 'Unauthorized Material',
            'content': 'Content',
            'price': '9.99',
            'subject': 'math',
            'material_type': 'document'
        })
        self.assertEqual(response.status_code, 302)  # 应该重定向到登录页面

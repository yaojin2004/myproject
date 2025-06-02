from django.test import TestCase, Client
from django.urls import reverse
from user_center.models import User
from .models import ReservationPost, ReservationOrder
from decimal import Decimal

class ReservationTests(TestCase):
    def setUp(self):
        self.client = Client()
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            phone='13800138000'
        )
        # 创建测试预约服务
        self.reservation = ReservationPost.objects.create(
            title='Test Service',
            content='Test Content',
            price=Decimal('99.99'),
            author=self.user,
            service_time='2024-01-01 14:00',
            location='Online',
            max_participants=5,
            current_participants=0,
            service_duration='2 hours'
        )
        self.create_url = reverse('reservation:create_reservation_post')
        self.detail_url = reverse('reservation:reservation_detail', 
                                kwargs={'post_id': self.reservation.id})

    def test_create_reservation(self):
        """测试创建预约服务"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.create_url, {
            'title': 'New Service',
            'content': 'New Content',
            'price': '199.99',
            'service_time': '2024-02-01 15:00',
            'location': 'Online',
            'max_participants': 3,
            'service_duration': '1 hour'
        })
        self.assertEqual(response.status_code, 302)  # 应该重定向到详情页
        self.assertTrue(ReservationPost.objects.filter(title='New Service').exists())

    def test_make_reservation(self):
        """测试预约服务"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('reservation:reserve', 
                                          kwargs={'post_id': self.reservation.id}))
        self.assertEqual(response.status_code, 302)  # 应该重定向到订单页面
        
        # 验证订单是否创建
        order = ReservationOrder.objects.filter(
            post=self.reservation,
            user=self.user
        ).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.price, self.reservation.price)

    def test_reservation_capacity(self):
        """测试预约人数限制"""
        self.client.login(username='testuser', password='testpass123')
        
        # 创建一个已满的预约服务
        full_service = ReservationPost.objects.create(
            title='Full Service',
            content='Test Content',
            price=Decimal('99.99'),
            author=self.user,
            service_time='2024-01-01 14:00',
            location='Online',
            max_participants=1,
            current_participants=1,
            service_duration='2 hours'
        )
        
        # 尝试预约已满的服务
        response = self.client.post(reverse('reservation:reserve', 
                                          kwargs={'post_id': full_service.id}))
        self.assertEqual(response.status_code, 400)  # 应该返回错误

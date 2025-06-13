from django.urls import path
from . import views
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'user_center'
urlpatterns = [
    path('', views.login_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('register/step2/', views.register_step2, name='register_step2'),
    path('send-verification-code/', views.send_verification_code, name='send_verification_code'),
    path('register1/', views.register1, name='register1'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    # path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    # path('create/', views.create_post, name='create_post')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls')
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/square/', permanent=False), name='home'),  # 添加根路径重定向
    path('admin/', admin.site.urls),
    # 包含user应用下的urls.py中的所有路由
    path("user_center/", include("user_center.urls"), name="user_center"),
    path("learn_post/", include("learn_post.urls"), name="learn_post"),
    path("square/", include("square.urls"), name="square"),
    path("send_post/", include("send_post.urls"), name="send_post"),
    path("reservation/", include("reservation.urls"), name="reservation"),
]

# 将静态文件和媒体文件的 URL 路径映射到它们在服务器上的根目录，从而使得在开发过程中可以通过 URL 访问这些文件
# 静态和媒体文件的URL配置
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
from . import views
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'reservation'

urlpatterns = [
    path('', views.reservation, name='reservation'),
    path('create/', views.create_reservation_post, name='create_reservation_post'),
    path('post/<int:post_id>/', views.reservation_detail, name='reservation_detail'),
    path('post/<int:post_id>/reserve/', views.reserve_post, name='reserve'),
    # path('create/', views.create_post, name='create_post')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

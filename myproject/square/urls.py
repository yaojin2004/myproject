from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'square'

urlpatterns = [
    path('', views.square, name='index'),
    path('post/<str:post_type>/<int:post_id>/', views.post_detail, name='post_detail'),
    path('purchase/<int:post_id>/', views.purchase_study_material, name='purchase_study_material'),
    path('download/<int:post_id>/', views.download_file, name='download_file'),
    path('reserve/<int:post_id>/', views.reserve_post, name='reserve_post'),
    path('comment/<int:post_id>/', views.post_comment, name='post_comment'),
    path('delete_post/<str:post_type>/<int:post_id>/', views.delete_post, name='delete_post'),
    # path('create/', views.create_post, name='create_post')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

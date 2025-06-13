from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'send_post'

urlpatterns = [
    path('', views.send_post, name='send_post'),
    path('learn_post/', views.learn_post_view, name='learn_post'),
    path('reservation/', views.reservation_post_view, name='reservation_post'),
    path('learn_post/create/', views.create_learn_post, name='create_learn_post'),
    path('reservation/create/', views.create_reservation_post, name='create_reservation_post'),
    path('create/study/', views.create_study_material, name='create_study_material'),
    path('learn_post/<int:post_id>/', views.learn_post_detail, name='learn_post_detail'),
    path('api/comments/add/<int:post_id>/', views.add_comment, name='add_comment'),
    # path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    # path('create/', views.create_post, name='create_post')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

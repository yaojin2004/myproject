from django.contrib import admin
from django.utils.html import format_html
from .models import StudyMaterialComment

@admin.register(StudyMaterialComment)
class StudyMaterialCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_title', 'user_name', 'short_content', 'created_time')
    list_filter = ('created_time',)
    search_fields = ('content', 'post__title', 'user__username')
    readonly_fields = ('created_time',)
    list_per_page = 20
    date_hierarchy = 'created_time'
    
    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = '学习资料'
    
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = '评论用户'
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = '评论内容'
    
    def has_add_permission(self, request):
        return False  # 禁止在管理界面添加评论

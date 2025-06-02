from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

class PostAdmin(admin.ModelAdmin):
    """基础帖子管理类，用于继承"""
    list_display = ('title', 'author', 'price', 'created_time')
    list_filter = ('created_time',)
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_time', 'update_time')
    list_per_page = 20
    date_hierarchy = 'created_time'

    def get_readonly_fields(self, request, obj=None):
        if obj:  # 编辑现有对象
            return self.readonly_fields + ('author',)
        return self.readonly_fields

from django.contrib import admin
from django.utils.html import format_html
from .models import ReservationPost, ReservationOrder, Reservation, Comment
from square.admin import PostAdmin

@admin.register(ReservationPost)
class ReservationPostAdmin(PostAdmin):
    list_display = PostAdmin.list_display + ('status', 'current_participants', 'max_participants')
    list_filter = ('status', 'created_time')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'content', 'author')
        }),
        ('服务详情', {
            'fields': ('service_time', 'service_duration', 'location', 'price', 'wechat')
        }),
        ('预约状态', {
            'fields': ('status', 'max_participants', 'current_participants')
        }),
        ('其他信息', {
            'fields': ('cover_image', 'created_time', 'update_time'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ReservationOrder)
class ReservationOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'post_title', 'user_name', 'price', 'status', 'created_time')
    list_filter = ('status', 'created_time')
    search_fields = ('order_number', 'post__title', 'user__username')
    readonly_fields = ('order_number', 'created_time', 'update_time')
    list_per_page = 20
    date_hierarchy = 'created_time'
    
    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = '预约服务'
    
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = '预约用户'

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_title', 'user_name', 'status', 'created_time')
    list_filter = ('status', 'created_time')
    search_fields = ('post__title', 'user__username')
    readonly_fields = ('created_time',)
    list_per_page = 20
    date_hierarchy = 'created_time'
    
    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = '预约服务'
    
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = '预约用户'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_title', 'user_name', 'short_content', 'created_time')
    list_filter = ('created_time',)
    search_fields = ('content', 'post__title', 'user__username')
    readonly_fields = ('created_time',)
    list_per_page = 20
    date_hierarchy = 'created_time'
    
    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = '预约服务'
    
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = '评论用户'
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = '评论内容'

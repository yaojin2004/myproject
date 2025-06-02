from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import AppointmentPost, StudyMaterialPost, Purchase, Comment

@admin.register(StudyMaterialPost)
class StudyMaterialPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'subject', 'material_type', 'price', 'created_time', 'show_image')
    list_filter = ('subject', 'material_type', 'created_time')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_time', 'update_time', 'show_image')
    list_per_page = 20
    date_hierarchy = 'created_time'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'content', 'author')
        }),
        ('资料信息', {
            'fields': ('subject', 'material_type', 'price')
        }),
        ('资料文件', {
            'fields': ('image', 'show_image', 'file', 'file_url')
        }),
        ('其他信息', {
            'fields': ('created_time', 'update_time'),
            'classes': ('collapse',)
        }),
    )
    
    def show_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return '无图片'
    show_image.short_description = '封面预览'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 编辑现有对象
            return self.readonly_fields + ('author',)
        return self.readonly_fields

@admin.register(AppointmentPost)
class AppointmentPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'appointment_time', 'price', 'status', 'current_people', 'people_limit', 'created_time')
    list_filter = ('status', 'created_time')
    search_fields = ('title', 'content', 'author__username', 'location')
    readonly_fields = ('created_time', 'update_time', 'show_image')
    list_per_page = 20
    date_hierarchy = 'created_time'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'content', 'author')
        }),
        ('预约详情', {
            'fields': ('appointment_time', 'location', 'price', 'wechat')
        }),
        ('人数控制', {
            'fields': ('status', 'people_limit', 'current_people')
        }),
        ('其他信息', {
            'fields': ('image', 'show_image', 'created_time', 'update_time'),
            'classes': ('collapse',)
        }),
    )
    
    def show_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return '无图片'
    show_image.short_description = '图片预览'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 编辑现有对象
            return self.readonly_fields + ('author',)
        return self.readonly_fields

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('buyer_name', 'seller_name', 'post_title', 'price', 'purchase_time')
    list_filter = ('purchase_time',)
    search_fields = ('buyer__username', 'seller__username', 'post_title')
    readonly_fields = ('purchase_time',)
    list_per_page = 20
    date_hierarchy = 'purchase_time'
    
    def buyer_name(self, obj):
        return obj.buyer.username
    buyer_name.short_description = '购买者'
    
    def seller_name(self, obj):
        return obj.seller.username
    seller_name.short_description = '出售者'
    
    def has_add_permission(self, request):
        return False  # 禁止在管理界面添加购买记录

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_title', 'user_name', 'short_content', 'created_time')
    list_filter = ('created_time',)
    search_fields = ('content', 'post__title', 'user__username')
    readonly_fields = ('created_time', 'updated_time')
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

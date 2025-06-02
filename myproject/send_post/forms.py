from django import forms
from .models import StudyMaterialPost

class StudyMaterialPostForm(forms.ModelForm):
    class Meta:
        model = StudyMaterialPost
        fields = ['title', 'content', 'subject', 'material_type', 'image', 'file', 'file_url', 'price']
        exclude = ['author', 'created_time', 'update_time']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入标题'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '请详细描述学习资料的内容',
                'rows': 5
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control'
            }),
            'material_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'file_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入资料链接'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入价格',
                'step': '0.01',
                'min': '0'
            })
        }

    def clean_file_url(self):
        url = self.cleaned_data.get('file_url')
        if url and not (url.startswith('http://') or url.startswith('https://')):
            raise forms.ValidationError('请输入有效的网络链接（以 http:// 或 https:// 开头）')
        return url

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('图片大小不能超过5MB')
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError('请上传有效的图片文件')
        return image

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance 
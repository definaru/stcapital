from django import forms
from ckeditor.widgets import CKEditorWidget
from stc.models import *


class ArticlesAdminForm(forms.ModelForm):
    header = forms.CharField(
        label="Заголовок",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Заголовок статьи...",
                "class": "form-control"
            }
        )
    )
    text = forms.CharField(label='Текст статьи', widget=CKEditorWidget())
    class Meta:
        model = Articles
        fields = '__all__'


class SeoAdminForm(forms.ModelForm):
    image = forms.CharField(
        label="Картинка страницы", 
        widget=forms.TextInput(
            attrs={
                "placeholder": "Вставьте ссылку на картинку...",
                "style": "width: 32%"
            }
        )
    )
    description = forms.CharField(
        label="Описание",
        help_text="Описание должно быть не более 200 символов, остальной текст не будет виден в поисковой выдаче", 
        widget=forms.Textarea(attrs={
            "placeholder": "Краткое описание статьи", 
            "cols": "76", 
            "rows": "5", 
            "style": "resize: none"
        })
    )
    class Meta: 
        model = SeoBlock
        fields = '__all__'

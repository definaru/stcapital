from django.contrib import admin
from django.shortcuts import render
from django.utils.html import format_html
from stc.forms import ArticlesAdminForm, SeoAdminForm
from stc.models import Profile, Category, Articles, SeoBlock, Account, Contact, UserLogin, Note, Transaction
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.conf import settings
from datetime import datetime
from user_agents import parse
'''
https://github.com/django/django/tree/main/django/contrib/admin/templates/admin
'''


def get_fancy_header():
    hour = datetime.now().hour
    if hour >= 0 and hour < 5: 
        time = "Доброй ночи"
    elif hour >= 10 and hour < 18: 
        time = "Добрый день"
    elif hour >= 18 and hour < 24:
        time = "Добрый вечер"
    else: 
        time = "Доброе утро"
    return time

admin.site.site_header = settings.HEADER
admin.site.site_title = get_fancy_header()
admin.site.index_title = settings.DESCRIPTION



@admin.register(UserLogin)
class UserLoginAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'user_agent']
    fields = ['user', 'login_time', 'device_info']
    readonly_fields = ["login_time"]

    @admin.display(description='Устройство')
    def user_agent(self, obj):
        user_agent = parse(obj.device_info)
        return mark_safe(f'<b>{str(user_agent)}</b>')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'summa', 'currency', 'due_date', 'is_payment', 'datetime']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'alternative', 'slug']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['number', 'user', 'name', 'price', 'currency', 'status', 'date']
    list_filter = ('user', 'status') 

    @admin.display(description='Текущая валюта')
    def number(self, obj):
        return mark_safe(f'<a href="/admin/stc/transaction/{obj.id}/change/">#{obj.payment}</a>')


@admin.register(SeoBlock)
class SeoBlockAdmin(admin.ModelAdmin):
    #list_display = ['robots', 'type', 'image', 'title', 'description', 'keywords']
    empty_value_display = "-empty-"
    form = SeoAdminForm


class ContactInstanceInline(admin.TabularInline):
    model = Contact


class NoteInstanceInline(admin.TabularInline):
    model = Note


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_public', 'link', 'user']
    list_display_links = ["name"]


@admin.register(Articles)
class ArticlesAdmin(admin.ModelAdmin):
    search_fields = ["header"]
    list_display = ['preview', 'header', 'language', 'category', 'datetime', 'is_public']
    list_display_links = ["header"]
    prepopulated_fields = {"link": ["header"]}
    form = ArticlesAdminForm
    fields = ['seo', 'header', 'view', 'text', 'language', 'category', 'datetime', 'user', 'link', 'is_public']
    readonly_fields = ["view"]
    list_per_page = 10
    list_filter = ('language', 'category', 'is_public') 

    @admin.display(description='Превью')
    def view(self, obj):
        if obj.photo:
            photo = obj.photo
        else: 
            photo = '/media/images/no_photo.jpg'
        return mark_safe(f'<img src="{photo}" alt="{obj.header}" class="readonly_articles_image" />')
    
    @admin.display(description='Картинка')
    def preview(self, obj):
        if obj.photo:
            photo = obj.photo
        else: 
            photo = '/media/images/no_photo.jpg'
        return mark_safe(f'<img src="{photo}" alt="{obj.header}" class="image_previev" />')
    

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['get_avatar', 'name', 'href', 'email', 'get_account', 'datetime']
    list_display_links = ["get_avatar", "name"]
    inlines = [
        NoteInstanceInline, 
        ContactInstanceInline
    ]

    @admin.display(description='ФИО')
    def name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'
    
    @admin.display(description='Фото')
    def get_avatar(self, obj):
        if obj.avatar:
            photo = obj.avatar.url
        else: 
            photo = '/media/images/no_photo.jpg'
        return mark_safe(f'<img src="{photo}" alt="{self.name}" class="image_previev" />')
    
    @admin.display(description='Тариф')
    def get_account(self, obj):
        return mark_safe(f'<span class="badge badge-success">{obj.account.name}</span>')
    
    @admin.display(description='Дата добавления')
    def datetime(self, obj):
        return obj.user.date_joined
    
    @admin.display(description='E-mail')
    def email(self, obj):
        return mark_safe(f'<a href="mailto:{obj.user.email}" target="_blank">{obj.user.email}</a>')


class UserInline(admin.StackedInline):
    model = Profile
    readonly_fields = ["preview"]
    can_delete = False
    verbose_name_plural = 'Доп. информация'

    @admin.display(description='Аватарка')
    def preview(self, obj): # avatar
        return mark_safe(f'<img src="{obj.avatar.url}">')
 


# Определяем новый класс настроек для модели User
class UserAdmin(UserAdmin):
    inlines = (UserInline, )


# Перерегистрируем модель User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
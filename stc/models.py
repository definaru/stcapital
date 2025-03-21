from django.db import models 
from datetime import datetime
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from stc.data.datalist import LIST_OF_LANGUAGE, ROBOTS, TYPE_PAGE, TYPE_CURRENCY, NAME_PLAN, DUE_DATE, LIST_CONTACTS, LIST_STATUS


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def user_id():
    since = int(datetime.now().timestamp())
    return f'id00{since}'


class UserLogin(models.Model): 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    device_info = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'сессии'
        verbose_name_plural = 'Сессии пользователей'


class Category(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=255, null=True, verbose_name='Название категории')
    alternative = models.CharField(max_length=255, null=True, verbose_name='Версия на испанском')
    slug = models.CharField(
        max_length=64, 
        null=False, 
        verbose_name='Версия на английском', 
        help_text='Английское название для мультиязычности'
    )

    class Meta:
        verbose_name = 'категорию'
        verbose_name_plural = 'Список категорий'
    
    def __str__(self):
        return self.name

   
class SeoBlock(models.Model):
    id = models.AutoField(primary_key = True)
    robots = models.CharField(max_length=255, default='index, follow', null=False, verbose_name='Метатег robots', choices=ROBOTS)
    type = models.CharField(max_length=64, default='website', null=False, verbose_name='Тип страницы', choices=TYPE_PAGE)
    image = models.CharField(max_length=255, null=True, verbose_name='Картинка страницы')
    title = models.CharField(null=False, verbose_name='Заголовок страницы')
    description = models.CharField(max_length=200, null=False, verbose_name='Описание страницы')
    keywords = models.CharField(
        max_length=255, 
        null=True, 
        verbose_name='Ключевые слова',
        help_text='Слова в единственном числе, через запятую, которые встречаются в тексте, не более 200 символов.'
    )

    class Meta:
        verbose_name = 'SEO'
        verbose_name_plural = 'SEO-оптимизация'
    
    def __str__(self):
        return self.title
    

class Articles(models.Model):
    id = models.AutoField(primary_key = True)
    seo = models.ForeignKey(SeoBlock, null=True, on_delete = models.CASCADE, related_name='seo', verbose_name='Meta-теги')
    header = models.CharField(max_length=255, null=True, verbose_name='Заголовок')
    photo = models.ImageField(max_length=255, upload_to='images/blog', null=True, verbose_name='Фотография статьи')
    text = models.CharField(null=False, verbose_name='Текст статьи')
    language = models.CharField(max_length=64, null=False, verbose_name='Язык статьи', choices=LIST_OF_LANGUAGE)
    category = models.ForeignKey(Category, null=True, on_delete = models.CASCADE, related_name='category', verbose_name='Категория статьи')
    link = models.CharField(
        max_length=255, 
        null=False, 
        verbose_name='Ссылка на статью', 
        help_text='Английское название без пробелов и дефисов, только нижнее подчёркивание'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog', verbose_name='ID пользователя')
    datetime = models.DateTimeField(verbose_name='Дата создания')
    is_public = models.BooleanField(verbose_name='Статус публикации')

    class Meta:
        ordering = ['-datetime']
        verbose_name = 'статью'
        verbose_name_plural = 'Список статей'
    
    def __str__(self):
        return self.header
    

class Account(models.Model):
    id = models.AutoField(primary_key = True)
    summa = models.CharField(max_length=255, null=False, verbose_name='Сумма')
    currency = models.CharField(max_length=64, null=False, verbose_name='Текущая валюта', choices=TYPE_CURRENCY)
    name = models.CharField(max_length=255, null=False, verbose_name='Название тарифа', choices=NAME_PLAN, default='Free')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    due_date = models.CharField(max_length=255, null=False, verbose_name='Срок оплаты', choices=DUE_DATE, default='3')
    is_payment = models.BooleanField(verbose_name='Статус оплаты')
    datetime = models.DateTimeField(verbose_name='Дата создания')

    class Meta:
        verbose_name = 'аккаунт'
        verbose_name_plural = 'Список аккаунтов'

    def __str__(self):
        return f'Тариф: {self.name}'



class Profile(models.Model):
    id = models.AutoField(primary_key = True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='photo')
    avatar = models.ImageField(max_length=255, upload_to='images/users', verbose_name='Фотография')
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='account')
    background = models.ImageField(max_length=255, upload_to='images/users/bg', blank=True, null=True, verbose_name='Фон')
    href = models.CharField(
        max_length=255, 
        null=False, 
        verbose_name='Юзернейм',
        default=user_id()
    )

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    



class Contact(models.Model):
    id = models.AutoField(primary_key = True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user', verbose_name='ID пользователя')
    name = models.CharField(max_length=255, null=False, verbose_name='Тип контакта', choices=LIST_CONTACTS)
    is_public = models.BooleanField(verbose_name='Публичный')
    link = models.CharField(max_length=255, null=False, verbose_name='Ссылка на ресурс')
    profile = models.ForeignKey(Profile, related_name='contacts', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = 'контакты'
        verbose_name_plural = 'Список контактов'



class Note(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Profile, related_name='notes', on_delete=models.CASCADE)
    user_position = models.CharField(verbose_name='Должность / Специальность', max_length=255)
    description = models.TextField(verbose_name='Описание о себе')
    language = models.CharField(max_length=64, null=False, verbose_name='Язык заметки', choices=LIST_OF_LANGUAGE)

    class Meta:
        verbose_name = 'Описание'
        verbose_name_plural = 'Список данных'

    def __str__(self):
        return f'{self.user_position} ({self.language})'
    


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    name = models.CharField(max_length=255, null=False, verbose_name='Название тарифа', choices=NAME_PLAN, default='Free')
    price = models.CharField(max_length=200, verbose_name='Цена')
    currency = models.CharField(max_length=64, null=False, verbose_name='Текущая валюта', choices=TYPE_CURRENCY)
    payment = models.CharField(max_length=255, verbose_name='№ платежа', null=True, blank=True)
    status = models.CharField(max_length=20, choices=LIST_STATUS, default='pending', verbose_name='Статус')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата транзакции')

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Список транзакций'

    def __str__(self):
        return f'Транзакция {self.id}'
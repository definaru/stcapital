import secrets, requests
from django.shortcuts import get_object_or_404, render
from string import ascii_lowercase, ascii_uppercase, digits
from django.http import JsonResponse
from django.contrib.auth.models import User
from stc.models import *
from stc.serializers import TransactionSerializer, UserSerializer, CategorySerializer, ArticlesSerializer, ProfileSerializer, AccountSerializer
from django.core.mail import EmailMultiAlternatives
from rest_framework import status, viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string
from rest_framework.authtoken.models import Token
from django.utils.dateparse import parse_datetime
from django.conf import settings
from datetime import datetime
from .translation import NameTranslator



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Успешный выход из системы.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]
    renderer_classes = [JSONRenderer] 


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, ]
    renderer_classes = [JSONRenderer] 



class TransactionViewSet(viewsets.ModelViewSet):
    #queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, ]
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        queryset = Transaction.objects.all().order_by('-date')
        return queryset
    
    @action(detail=False, methods=['get'], url_path='(?P<username>[^/.]+)')
    def get_by_username(self, request, username=None):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        user = get_object_or_404(User, username=username)
        queryset = self.get_queryset().filter(user=user)

        if start_date:
            start_date = parse_datetime(start_date)
            queryset = queryset.filter(date__gte=start_date)

        if end_date:
            end_date = parse_datetime(end_date)
            queryset = queryset.filter(date__lte=end_date)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    renderer_classes = [JSONRenderer] 


class ArticlesViewSet(viewsets.ModelViewSet):
    serializer_class = ArticlesSerializer
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        return Articles.objects.all().order_by('id')
    
    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        article = get_object_or_404(queryset, pk=pk)
        serializer = ArticlesSerializer(article, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='(?P<language>[^/.]+)/(?P<link>[^/.]+)')
    def get_by_language_and_link(self, request, language=None, link=None):
        queryset = self.get_queryset()
        article = get_object_or_404(queryset, language=language, link=link)
        serializer = ArticlesSerializer(article, context={'request': request})
        return Response(serializer.data)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    renderer_classes = [JSONRenderer]
    lookup_field = 'href'

    def get_queryset(self):
        return Profile.objects.all().order_by('id')
    
    def retrieve(self, request, href=None):
        queryset = self.get_queryset()
        profile = get_object_or_404(queryset, href=href)
        lang = request.query_params.get('lang', 'ru')
        translator = NameTranslator(to_lang=lang)
        profile.user.first_name = translator.translate_name(profile.user.first_name)
        profile.user.last_name = translator.translate_name(profile.user.last_name)
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='(?P<lang>[^/.]+)/(?P<href>[^/.]+)')
    def get_by_lang_and_href(self, request, lang=None, href=None):
        if lang is None or href is None:
            return Response(
                {"detail": "Both 'lang' and 'href' parameters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        queryset = self.get_queryset()
        profile = get_object_or_404(queryset, href=href)
        translator = NameTranslator(to_lang=lang)
        profile.user.first_name = translator.translate_name(profile.user.first_name)
        profile.user.last_name = translator.translate_name(profile.user.last_name)
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)



@api_view(['POST'])
def resetPassword(request):
    if request.method == 'POST':
        to_email = request.data.get('email')
        subject = 'Восстановление пароля'
        from_email = settings.EMAIL_HOST_USER

        user = User.objects.filter(email=to_email)
        data = {
            'email': to_email,
            'password': generate_password(20),
            'name': settings.HEADER,
            'support_mail': settings.DEFAULT_SUPPORT_EMAIL,
            'support_phone': settings.DEFAULT_PHONE,
            'user': user.first()
        }

        isvalid = user.exists()
        if isvalid:
            arr = {
                'header': 'Отлично! Проверьте почту.',
                'message': 'Мы отправили новый пароль на вашу почту',
                'email': to_email,
                'is_valid': isvalid
            }
            html_content = render_to_string('mail/resetpassword.html', data)
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)                
        else: 
            arr = {
                'header': 'Ошибка!',
                'message': 'Нет такого пользователя, или почта указана не верно',
                'email': to_email,
                'is_valid': isvalid
            }
        return JsonResponse(arr, safe=False)
    

def domain(request):
    url = request.META.get('HTTP_HOST')
    protocol = request.scheme
    return protocol+'://'+url


def index(request):
    arr = [
        {
            'name': settings.HEADER,
            'description': settings.DESCRIPTION,
            'version': '0.1.9',
            'domain': '',
            'info': domain(request)+'/info',
            'api': domain(request)+'/api/v1/?format=json',
            'support': {
                'text': 'Служба технической поддержки',
                'phone': settings.DEFAULT_PHONE,
                'email': settings.DEFAULT_SUPPORT_EMAIL                
            }
        }
    ]
    return JsonResponse(arr[0], safe=False)


def is_error_user():
    error = {
        'error': True,
        'message': 'Пользователь не авторизован',
        'type': 'error',
        'color': 'danger'
    }
    return JsonResponse(error, safe=False)


def current_user(request, token):
    auth = Token.objects.filter(key=token).values()
    if not auth:
        return is_error_user()
    else:
        user_id = list(auth)[0]['user_id']
        response = User.objects.filter(id=user_id).values(
            'id', 
            'is_superuser', 
            'last_login',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_active'
        )
        return JsonResponse(list(response)[0], safe=False)
    

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def getGeolocation(request):
    #ip = get_client_ip(request)
    url = "https://ipapi.co/54.39.207.190/json/"
    payload = {}
    headers = {
        'Content-Type': 'application/json; charset=UTF-8'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return JsonResponse(response.json(), safe=False)


def info(request):
    ip = request.META.get('REMOTE_ADDR')
    #ip = get_client_ip(request)
    useragent = request.META.get('HTTP_USER_AGENT')
    username = request.META.get('USERNAME')
    data = [ # https://pypi.org/project/user-agents/
        {
            'ip': ip,
            'debug': settings.DEBUG,
            'datetime': datetime.now(),
            'base_dir': settings.BASE_DIR,
            'languages': settings.LANGUAGE_CODE,
            'time_zone': settings.TIME_ZONE,
            'useragent': useragent,
            'username': username,
            #'location': getGeolocation(request)
        }
    ]
    return JsonResponse(list(data)[0], safe=False)


def page_not_found(request, exception):
    arr = {
        'header': 'Ошибка 404',
        'message': 'Нет такой страницы',
        'color': 'danger'
    }
    return JsonResponse(arr, safe=False)


def generate_password(length):
    letters = ascii_lowercase+ascii_uppercase+digits
    password = ''.join(secrets.choice(letters) for i in range(length))
    return password
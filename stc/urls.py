from django.contrib import admin
from django.conf.urls import handler404
from django.urls import include, path, re_path
from rest_framework import routers
from stc.token import CustomAuthToken
from django.conf import settings
from django.views.static import serve
from . import views



router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'category', views.CategoryViewSet)
router.register(r'articles', views.ArticlesViewSet, basename='article')
router.register(r'profile', views.ProfileViewSet, basename='profile')
router.register(r'account', views.AccountViewSet)
router.register(r'transaction', views.TransactionViewSet, basename='transaction')
handler404 = 'stc.views.page_not_found'


urlpatterns = [
    path('', views.index, name="home"),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^assets/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/v1/token/auth/', CustomAuthToken.as_view()),
    path('api/v1/logout/', views.user_logout, name='logout'),
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('api/v1/me/<str:token>', views.current_user),
    path('api/v1/reset/password', views.resetPassword),
    path('api/v1/geo/location', views.getGeolocation),
    path('info', views.info)
]
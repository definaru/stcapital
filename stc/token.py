from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from stc.models import UserLogin
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        useragent = request.META.get('HTTP_USER_AGENT')
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        UserLogin.objects.create(user=user, device_info=useragent)

        if not useragent:
            return Response({
                'status': 403,
                'message': 'Доступ запрещён',
                'error': 'Unable to determine USER AGENT, a bot may have logged in'
            })
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'username': '@'+user.username, 
            'first_name': user.first_name, 
            'last_name': user.last_name,
        })
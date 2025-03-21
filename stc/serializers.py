from rest_framework import serializers
from stc.models import *
from django.contrib.auth.models import User, Group


class GroupSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Group
        fields = ['name']


class UserArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class UserSerializer(
        serializers.HyperlinkedModelSerializer, 
        serializers.ModelSerializer
    ):
    # serializer = serializers.StringRelatedField() #
    #position = serializers.StringRelatedField(many=True)
    #groups = GroupSerializer(many=True)

    class Meta:
        model = User
        fields = [ #'groups', 
            'username', 'first_name', 'last_name', 'email', 'is_superuser', 'is_staff', 'is_active'
        ]



class SeoBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeoBlock
        fields = ['robots', 'type', 'image', 'title', 'description', 'keywords']



class CategorySerializer(
        serializers.HyperlinkedModelSerializer, 
        serializers.ModelSerializer
    ):
    class Meta:
        model = Category
        fields = '__all__'



class ArticlesSerializer(
        serializers.HyperlinkedModelSerializer, 
        serializers.ModelSerializer
    ):
    seo = SeoBlockSerializer()
    category = CategorySerializer()
    user = UserArticleSerializer()
    photo = serializers.StringRelatedField()

    class Meta:
        model = Articles
        fields = ['seo', 'header', 'photo', 'text', 'language', 'category', 'link', 'user', 'datetime', 'is_public']



class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'is_public', 'link']



class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['user_position', 'description', 'language']



class ProfilePhotoSerializer(serializers.ModelSerializer):
    user = UserArticleSerializer()
    class Meta:
        model = Profile
        fields = ['user', 'avatar', 'account', 'background', 'href', 'contacts']



class AccountSerializer(serializers.ModelSerializer):
    user = UserArticleSerializer()
    
    class Meta:
        model = Account
        fields = ['summa', 'currency', 'name', 'due_date', 'is_payment', 'datetime', 'user']



class AccountProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['summa', 'currency', 'name', 'due_date', 'is_payment', 'datetime']



class TransactionSerializer(serializers.ModelSerializer):
    user = UserArticleSerializer()

    class Meta:
        model = Transaction
        fields = ['name', 'price', 'currency', 'payment', 'status', 'user', 'date']



class ProfileSerializer(serializers.ModelSerializer):
    user = UserArticleSerializer()
    account = AccountProfileSerializer()
    contacts = ContactSerializer(many=True)
    notes = NoteSerializer(many=True)

    class Meta:
        model = Profile
        fields = ['user', 'avatar', 'notes', 'account', 'background', 'href', 'contacts']
        # lookup_field = 'href'
        # extra_kwargs = {
        #     'url': {'lookup_field': 'href'}
        # }
        
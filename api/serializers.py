from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import BaseModel, Article

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseModel
        fields = ['id', 'user']


class ArticleSerializer(BaseModelSerializer):
    class Meta:
        model = Article
        fields = BaseModelSerializer.Meta.fields + ['name', 'article']

from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from api.models import BaseModel, Article, CustomUser, Video, Comment


class CustomUserSerializer(UserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password']


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseModel
        fields = ['id', 'user']


class ArticleSerializer(BaseModelSerializer):
    class Meta:
        model = Article
        fields = BaseModelSerializer.Meta.fields + ['name', 'article']


class VideoSerializer(BaseModelSerializer):
    class Meta:
        model = Video
        fields = BaseModelSerializer.Meta.fields + ['name', 'url']


class CommentSerializer(BaseModelSerializer):
    class Meta:
        model = Comment
        fields = BaseModelSerializer.Meta.fields + ['comment']

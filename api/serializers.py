from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from api.models import BaseModel, Article, CustomUser, Video, Comment


class CustomUserSerializer(UserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password']


class BaseModelSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='user.id', read_only=True)

    class Meta:
        model = BaseModel
        fields = ['id', 'user_id']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ArticleSerializer(BaseModelSerializer):
    class Meta:
        model = Article
        fields = BaseModelSerializer.Meta.fields + ['name', 'article']

    def validate_name(self, value):
        if len(value) < 5:
            raise serializers.ValidationError('Длинна наименования поста должна быть больше 5')

        if len(value) > 255:
            raise serializers.ValidationError('Длинна наименования поста должна быть меньше 255')


class VideoSerializer(BaseModelSerializer):
    class Meta:
        model = Video
        fields = BaseModelSerializer.Meta.fields + ['name', 'url']

    def validate_name(self, value):
        if len(value) < 5:
            raise serializers.ValidationError('Длинна наименования видео должна быть больше 5')

        if len(value) > 255:
            raise serializers.ValidationError('Длинна наименования видео должна быть меньше 255')


class CommentSerializer(BaseModelSerializer):
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(),
        source='article',
        write_only=True,
        required=False,
        allow_null=True
    )
    video_id = serializers.PrimaryKeyRelatedField(
        queryset=Video.objects.all(),
        source='video',
        write_only=True,
        required=False,
        allow_null=True
    )

    article = ArticleSerializer(read_only=True)
    video = VideoSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = BaseModelSerializer.Meta.fields + ['comment', 'article', 'video', 'article_id', 'video_id']


class CommentListSerializer(BaseModelSerializer):

    class Meta:
        model = Comment
        fields = BaseModelSerializer.Meta.fields + ['comment', 'article_id', 'video_id']

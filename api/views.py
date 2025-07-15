from api.base_view_set import BaseViewSet
from api.models import Article, Video, Comment
from api.serializers import ArticleSerializer, VideoSerializer, CommentSerializer


class ArticleViewSet(BaseViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    search_fields = ['name', 'article']
    table_name = Article._meta.db_table


class VideoViewSet(BaseViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    search_fields = ['name', 'url']
    table_name = Video._meta.db_table


class CommentViewSet(BaseViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    search_fields = ['comment']
    table_name = Comment._meta.db_table

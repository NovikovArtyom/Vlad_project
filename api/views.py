from django.core.mail import send_mail
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from api.base_view_set import BaseViewSet
from api.models import Article, Video, Comment, CustomUser, Role
from api.serializers import ArticleSerializer, VideoSerializer, CommentSerializer, CommentListSerializer, \
    CustomUserSerializer


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

    def get_serializer_class(self):
        if self.action == 'list':
            return CommentListSerializer
        return CommentSerializer


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def list(self, request, *args, **kwargs):
        admin_role = Role.objects.get(title='ADMIN')
        if admin_role not in request.user.role.all():
            raise PermissionDenied(
                "У вас нет прав для получения списка пользователей",
                code=status.HTTP_403_FORBIDDEN
            )
        return super(UsersViewSet, self).list(request, *args, **kwargs)


class SendEmailView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            send_mail(
                'Тестовое письмо',
                'Тестовое письмо',
                None,
                ['artyom.nov.1997@gmail.com'],
                fail_silently=False,
            )
            return Response(
                {'data': 'Email отправлен успешно'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'data': 'error'}
            )

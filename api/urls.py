from django.urls import path, include
from rest_framework.routers import SimpleRouter

from api.views import ArticleViewSet, VideoViewSet, CommentViewSet, SendEmailView

router = SimpleRouter()
router.register('article', ArticleViewSet)
router.register('video', VideoViewSet)
router.register('comment', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('email/', SendEmailView.as_view()),
]

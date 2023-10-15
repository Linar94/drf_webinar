from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from api.views import PostViewSet, CommentViewSet, SubscribeApiView, set_stars

v1_router = DefaultRouter()
v1_router.register("post", PostViewSet, basename='v1_post')
v1_router.register("comment", CommentViewSet, basename='v1_comment')

jwt_patterns = [
    path('create/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
]

urlpatterns = v1_router.urls
urlpatterns += v1_router.urls
urlpatterns += [
    path('jwt/', include(jwt_patterns)),
    path('subscribe/', SubscribeApiView.as_view(), name='v1_subscribe'),
    path('post/<str:post_id>/set-star/', set_stars, name='v1_set-star'),
]

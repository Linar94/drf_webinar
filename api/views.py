from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.decorators import permission_classes

from core.models import Comment, Post
from api.serializers import PostSerializer, CommentSerializer, FollowSerializer, StarSerializer


class PostViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Post.objects.select_related("group").prefetch_related("user_stars", "comments")
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ["get", "post", "patch", "delete"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated,)
    http_method_names = ["get", "post", "delete"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SubscribeApiView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)

    def post(self, request, format=None):
        follow_serializer = FollowSerializer(data=request.data, context={"request": request})
        follow_serializer.is_valid(raise_exception=True)
        follow_serializer.save()
        return Response(follow_serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def set_stars(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    serializer = StarSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save(post=post, user=request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

from django.db.models import Avg
from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault

from core.models import Comment, Follow, Group, Post, User, Star


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "first_name", "last_name")
        model = User


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        fields = '__all__'
        model = Comment


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author", read_only=True)
    group = GroupSerializer(read_only=False)
    comments = CommentSerializer(many=True, read_only=True)
    stars = serializers.SerializerMethodField()

    class Meta:
        fields = ("id", "published_at", "topic", "author_name", "text", "group", "comments", "stars")
        model = Post

    def create(self, validated_data):
        group = validated_data.pop("group")
        with atomic():
            group_obj = Group.objects.create(
                title=group["title"],
                slug=group["slug"],
                description=group["description"]
            )
            validated_data["group"] = group_obj
            return super(PostSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        group = validated_data.pop("group")
        with atomic():
            group_obj = instance.group
            instance = super(PostSerializer, self).update(instance, validated_data)
            group_obj.title = group["title"]
            group_obj.slug = group["slug"]
            group_obj.description = group["description"]
            group_obj.save(update_fields=["title", "slug", "description"])
            return instance

    def get_stars(self, obj):
        return obj.user_stars.aggregate(stars_avg=Avg("stars"))["stars_avg"] or 0


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username', default=CurrentUserDefault(), queryset=User.objects.all()
    )
    following = serializers.SlugRelatedField(
        read_only=False, slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')


class StarSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        instance, _ = Star.objects.update_or_create(
            post=validated_data["post"],
            user=validated_data["user"],
            defaults={"stars": validated_data["stars"]}
        )
        return instance

    def validate(self, attrs):
        if attrs.get("stars") and attrs["stars"] > 5:
            raise ValidationError({"stars": "Максимальная оценка не должна превышать 5 звезд"})
        return attrs

    stars = serializers.IntegerField(required=True)

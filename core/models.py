from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Group(models.Model):
    """ Модель для создания группы в соц.сети. """

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    """ Модель для создания поста в соц.сети. """
    topic = models.CharField(help_text="Введите тему поста", max_length=255, null=True)
    text = models.TextField(
        help_text="Введите текст поста",
        validators=[MaxLengthValidator(250, "Превышено максимальное количество символов")]
    )
    published_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text="Выберите группу поста"
    )

    class Meta:
        ordering = ('-published_at',)


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Избранный автор'
    )

    class Meta:
        unique_together = ('user', 'following')


class Star(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name="Пост", related_name="user_stars")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    stars = models.PositiveIntegerField(
        validators=[MaxValueValidator(250, "Превышено максимальное количество символов")],
        verbose_name="Количество звезд"
    )

    class Meta:
        unique_together = ('post', 'user')

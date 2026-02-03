from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Кастомная модель пользователя для Foodgram"""

    email = models.EmailField(
        'Email адрес',
        unique=True,
        max_length=254
    )
    first_name = models.CharField(
        'Имя',
        max_length=150
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/avatars/',
        blank=True,
        null=True
    )
    subscriptions = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='subscribers',
        verbose_name='Подписки',
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username

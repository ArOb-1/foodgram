from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from constants import (
    MAX_COOKING_TIME, MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT,
    MAX_LENGTH_LONG, MAX_LENGTH_SHORT, MAX_INGREDIENT_AMOUNT
)


User = get_user_model()


class Tag(models.Model):
    """Модель для тегов рецептов"""
    name = models.CharField(
        'Название тега',
        max_length=MAX_LENGTH_SHORT,
        unique=True
    )
    slug = models.SlugField(
        'Slug тега',
        max_length=MAX_LENGTH_SHORT,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для ингредиентов"""
    name = models.CharField(
        'Название ингредиента',
        max_length=MAX_LENGTH_LONG
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LENGTH_SHORT
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=MAX_LENGTH_LONG
    )
    image = models.ImageField(
        'Картинка рецепта',
        upload_to='recipes/images/'
    )
    text = models.TextField(
        'Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=f'Время приготовления должно'
                f' быть не менее {MIN_COOKING_TIME} минуты'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=f'Время приготовления не должно превышать'
                f' {MAX_COOKING_TIME} минут'
            )
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи Рецепт-Ингредиент с количеством"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message=f'Количество должно'
                f' быть не менее {MIN_INGREDIENT_AMOUNT}'
            ),
            MaxValueValidator(
                MAX_INGREDIENT_AMOUNT,
                message='Количество должно'
                f' быть не менее {MAX_INGREDIENT_AMOUNT}'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            )
        ]


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favourite'
            )
        ]


class ShoppingCart(models.Model):
    """Список покупок пользователя"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            )
        ]

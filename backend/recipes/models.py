from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField('Название',
                            unique=True,
                            max_length=150)
    color = models.CharField('HEX-код',
                             unique=True,
                             max_length=7)
    slug = models.SlugField('SLUG',
                            unique=True,
                            max_length=150)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название',
                            max_length=150)
    measurement_unit = models.CharField('Единица измерения',
                                        max_length=150)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient')]

    def __str__(self):
        return '{} - {}'.format(self.name,
                                self.measurement_unit)


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               related_name='recipes',
                               on_delete=models.CASCADE,
                               verbose_name='Автор')
    name = models.CharField('Название',
                            max_length=150)
    image = models.ImageField('Фото',
                              upload_to='recipes/images/')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientToRecipe',
                                         verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag,
                                  verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                1,
                message='Минимальное время приготовления 1 мин.'
            ),
            MaxValueValidator(
                1440,
                message='Максимальное время приготовления 1 день'
            )])

    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientToRecipe(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='ingredients_recipe',
                               verbose_name='Рецепты')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='ingredients_recipe',
                                   verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                1,
                message='Минимальное количество 1'
            ),
            MaxValueValidator(
                10000,
                message='Максимальное количество 10000'
            )])

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_ingredienttorecipe')]

    def __str__(self):
        return '{} - {}'.format(self.recipe.name,
                                self.ingredient.name)


class ShopList(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shop_list',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shop_list',
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shop_list')]

    def __str__(self):
        return '{} добавил {} в покупки'.format(self.user,
                                                self.recipe.name)


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorites',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorites',
                               verbose_name='Рецепты')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite')]

    def __str__(self):
        return '{} добавил {} в избранное'.format(self.user,
                                                  self.recipe.name)

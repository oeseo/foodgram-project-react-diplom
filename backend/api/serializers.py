from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    ReadOnlyField,
    SerializerMethodField
)

from api.validators import validate_following
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientToRecipe,
    Recipe,
    ShopList,
    Tag
)
from users.models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    lookup_field = 'username'

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated
                and Follow.objects.filter(user=user, author=obj.id).exists())


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    """Получение ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientToRecipeSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientToRecipe
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount')


class CreateIngredientSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientToRecipe
        fields = ('id',
                  'amount')


class RecipeMinifiedSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time')


class FollowSerializer(ModelSerializer):
    id = ReadOnlyField(source='author.id')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')

    def validate(self, data):
        data = validate_following(data, self.context.get('request').user)
        return data

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = None
        if recipes_limit:
            queryset = obj.author.recipes.all()[:int(recipes_limit)]
        else:
            queryset = obj.author.recipes.all()
        return RecipeMinifiedSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated
                and Follow.objects.filter(user=user, author=obj.id).exists())


class GetRecipeListSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    ingredients = IngredientToRecipeSerializer(many=True,
                                               source='ingredients_recipe')

    class Meta:
        model = Recipe
        fields = ('id',
                  'author',
                  'tags',
                  'ingredients',
                  'name',
                  'image',
                  'text',
                  'cooking_time',
                  'is_favorited',
                  'is_in_shopping_cart')
        read_only_fields = ('author',
                            'tags',
                            'is_favorited',
                            'is_in_shopping_cart')

    def get_ingredients(self, obj):
        ingredients = IngredientToRecipe.objects.filter(recipe=obj)
        return IngredientToRecipeSerializer(ingredients, many=True).data

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated
                and obj.shop_list.filter(user=user).exists())

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated
                and obj.favorites.filter(user=user).exists())


class CreateRecipeSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = CreateIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'tags',
                  'ingredients',
                  'text',
                  'image',
                  'cooking_time')

    @staticmethod
    def create_tags(tags, recipe):
        recipe.tags.add(*tags)

    @staticmethod
    def create_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            IngredientToRecipe.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(ingredients_data, recipe)
        self.create_tags(tags, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        tags_data = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags_data)
        self.create_ingredients(ingredients, instance)
        self.create_tags(tags_data, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return GetRecipeListSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class ShopListSerializer(ModelSerializer):
    class Meta:
        model = ShopList
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data

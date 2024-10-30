from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import CustomUserMixin
from api.pagination import CustomPaginator
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (
    CreateRecipeSerializer,
    CustomUserSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    ShopListSerializer,
    GetRecipeListSerializer,
    TagSerializer
)
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientToRecipe,
    Recipe,
    ShopList,
    Tag
)
from users.models import Follow, User


class TagViewSet(CustomUserMixin):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(CustomUserMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = IngredientFilter
    pagination_class = None


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPaginator
    lookup_field = 'id'

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        follower = Follow.objects.filter(user=request.user)
        page = self.paginate_queryset(follower)
        serializer = FollowSerializer(page,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            follower = Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(follower,
                                          context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        follower = get_object_or_404(Follow,
                                     user=user,
                                     author=author)
        follower.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPaginator
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = CreateRecipeSerializer(instance=serializer.instance,
                                            context={'request': self.request})

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=self.get_success_headers(serializer.data))

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetRecipeListSerializer
        return CreateRecipeSerializer

    @action(detail=True, methods=['POST'])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'recipe': recipe.id,
            'user': request.user.id
        }

        serializer = ShopListSerializer(data=data,
                                        context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        get_object_or_404(ShopList,
                          recipe__id=pk,
                          user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'recipe': recipe.id,
            'user': request.user.id
        }
        serializer = FavoriteSerializer(data=data,
                                        context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        get_object_or_404(Favorite,
                          recipe=get_object_or_404(Recipe, id=pk),
                          user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        ingredients = IngredientToRecipe.objects.filter(
            recipe__shop_list__user=request.user
        ).values('ingredient__name',
                 'ingredient__measurement_unit'
                 ).annotate(amount=Sum('amount'))

        shop_list = ''
        for ingredient in ingredients:
            name = ingredient.get('ingredient__name')
            unit = ingredient.get('ingredient__measurement_unit')
            amount = ingredient.get('amount')

            shop_list += '{} {} - {}\n'.format(name, unit, amount)

        filename = 'shop_list.txt'
        headers = {
            'Content-Disposition': 'attachment; filename={}'.format(filename)
        }

        return HttpResponse(shop_list,
                            content_type='text/plain; charset=UTF-8',
                            headers=headers)

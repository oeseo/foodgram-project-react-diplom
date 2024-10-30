from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientToRecipe,
    Recipe,
    ShopList,
    Tag
)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'color',
                    'slug')
    list_filter = ('name',)
    search_fields = ('name',
                     'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientToRecipeInlineAdmin(admin.TabularInline):
    model = IngredientToRecipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'author',
                    'favorites_count')
    list_filter = ('name',
                   'author__username',
                   'tags__name')
    search_fields = ('name',
                     'author__username',
                     'tags__name')
    readonly_fields = ('favorites_count',)
    inlines = [IngredientToRecipeInlineAdmin]

    def favorites_count(self, obj):
        return obj.favorites.count()

    favorites_count.short_description = 'Добавлено в избранное'


class ShopListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('recipe__tags',)
    search_fields = ('recipe__name',
                     'user__username')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('recipe__tags',)
    search_fields = ('recipe__name',
                     'user__username')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShopList, ShopListAdmin)
admin.site.register(Favorite, FavoriteAdmin)

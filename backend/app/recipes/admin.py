from django.contrib import admin

from app.recipes.models import Cart, Ingredient, IngredientAmount, Recipe, Tag


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit', )
    list_filter = ('name', )
    search_fields = ('name', )
    empty_value_display = '-пусто-'


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('pk', 'amount', 'ingredient', 'recipe', )
    list_filter = ('ingredient', 'recipe', )
    search_fields = ('recipe', )
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug', )
    list_filter = ('name', 'color', )
    search_fields = ('name', )
    empty_value_display = '-пусто-'


class TagInline(admin.TabularInline):
    model = Recipe.tags.through
    verbose_name = 'Тег'
    verbose_name_plural = 'Теги'


class RecipesInline(admin.StackedInline):
    model = Cart.recipes.through
    verbose_name = 'Рецепт'
    verbose_name_plural = 'Рецепты'


class LikesInline(admin.TabularInline):
    model = Recipe.likes.through
    verbose_name = 'Пользователь'
    verbose_name_plural = 'Добавили в избранное'


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    fk_name = 'recipe'
    verbose_name = 'Ингридиент'
    verbose_name_plural = 'Ингридиенты'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'image', 'text', 'cooking_time', 'author', )
    exclude = ('ingredients', 'tags', 'likes', )
    inlines = (IngredientAmountInline, TagInline, LikesInline, )
    list_filter = ('name', 'cooking_time', 'author', )
    search_fields = ('name', 'author', )
    empty_value_display = '-пусто-'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', )
    exclude = ('recipes', )
    inlines = (RecipesInline, )
    list_filter = ('user', )
    search_fields = ('user', )
    empty_value_display = '-пусто-'

from django.contrib.auth import get_user_model
from django_filters import CharFilter
from django_filters import FilterSet as DefaultFilterSet
from django_filters.rest_framework import (FilterSet,
                                           ModelChoiceFilter,
                                           AllValuesMultipleFilter,
                                           BooleanFilter)

from app.recipes.models import Recipe

User = get_user_model()


class RecipeFilter(FilterSet):
    author = ModelChoiceFilter(
        queryset=User.objects.all()
    )
    tags = AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_in_shopping_cart = BooleanFilter(
        method='cart_filter'
    )
    is_favorited = BooleanFilter(
        method='favorite_filter'
    )

    def favorite_filter(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(likes__id=self.request.user.id)
        return queryset

    def cart_filter(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(carts__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags']


class IngredientFilter(DefaultFilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='startswith'
    )

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.recipes.views import (IngredientReadOnlyViewSet,
                               RecipeViewSet,
                               TagRetrieveViewSet)

v1_router = DefaultRouter()

v1_router.register(
    'recipes',
    RecipeViewSet,
    basename='recipes'
)
v1_router.register(
    'tags',
    TagRetrieveViewSet,
    basename='tags'
)
v1_router.register(
    'ingredients',
    IngredientReadOnlyViewSet,
    basename='ingredients'
)

urlpatterns = [
    path('', include(v1_router.urls)),
]

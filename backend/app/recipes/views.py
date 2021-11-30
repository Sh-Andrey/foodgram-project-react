from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db.models.signals import post_save
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from app.recipes.filters import IngredientFilter, RecipeFilter
from app.recipes.models import Ingredient, IngredientAmount, Recipe, Tag, Cart
from app.recipes.permissions import IsAuthorOrReadOnly
from app.recipes.serializers import (IngredientSerializer, RecipeSerializer,
                                     TagSerializer)
from app.users.serializers import UserRecipeSerializer

User = get_user_model()


class TagRetrieveViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related(
        'author'
    ).prefetch_related('ingredients').all()
    serializer_class = RecipeSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['get', 'delete'],
        url_name='favorite',
        url_path=r'(?P<id>[\d]+)/favorite',
        pagination_class=None,
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipe, id=kwargs['id'])
        like = User.objects.filter(
            id=user.id,
            favourite_recipes=recipe
        ).exists()
        if request.method == 'GET' and not like:
            recipe.likes.add(user)
            serializer = UserRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE' and like:
            recipe.likes.remove(user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {
                'detail': 'Действие уже выполнено'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def create_cart(sender, instance, **kwargs):
        Cart.objects.get_or_create(user=instance)

    post_save.connect(create_cart, sender=User)

    @action(
        detail=False,
        methods=['get', 'delete'],
        url_name='shopping_cart',
        url_path=r'(?P<id>[\d]+)/shopping_cart',
        pagination_class=None,
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipe, id=kwargs['id'])
        is_added = User.objects.filter(
            id=user.id,
            cart__recipes=recipe
        ).exists()
        if request.method == 'GET' and not is_added:
            user.cart.recipes.add(recipe)
            serializer = UserRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE' and is_added:
            user.cart.recipes.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {
                'detail': 'Действие уже выполнено'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        methods=['get'],
        url_name='download_shopping_cart',
        url_path='download_shopping_cart',
        pagination_class=None,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        title = 'СПИСОК ПОКУПОК'
        pdf_title = 'СПИСОК ПОКУПОК ДЛЯ РЕЦЕПТОВ'

        user = request.user
        response = HttpResponse(content_type='application/pdf')
        content_disposition = f'attachment; filename={"shopping_list.pdf"}'
        response['Content-Disposition'] = content_disposition
        pdfmetrics.registerFont(TTFont('Dej', 'DejaVuSans.ttf'))
        pdf = Canvas(response)
        pdf.setTitle(pdf_title)
        pdf.setFont('Dej', 20)
        pdf.drawCentredString(290, 720, title)
        pdf.setFont('Dej', 16)
        pdf.line(30, 710, 565, 710)
        height = 670
        shopping_list = IngredientAmount.objects.filter(
            recipe__carts__user=user).values(
                'ingredient__name',
                'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by()

        for id, data in enumerate(shopping_list, start=1):
            pdf.drawString(50, height, text=(
                f'{id}. {data["ingredient__name"]} - {data["amount"]} '
                f'{data["ingredient__measurement_unit"]}'
            ))
            height -= 25
        pdf.showPage()
        pdf.save()
        return response

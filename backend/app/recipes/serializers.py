from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from app.recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from app.users.serializers import UserSerializer


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='id',
        queryset=Ingredient.objects.all()
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientAmount
        fields = ['id', 'name', 'measurement_unit', 'amount']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(id=request.user.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.carts.filter(user=request.user).exists()

    def to_representation(self, instance):
        self.fields['tags'] = TagSerializer(many=True)
        return super().to_representation(instance)

    def validate(self, data):
        ingredients = data['ingredients']
        available_ingredients = {}
        tags = data['tags']
        available_tags = {}
        for tag in tags:
            if tag in available_tags:
                raise ValidationError(
                    '?????????????????????????? ???????? ??????????????????????'
                )
            available_tags['tag'] = True

        for ingredient in ingredients:
            if ingredient['amount'] <= 0:
                raise ValidationError(
                    '???????????????????? ?????????????????????? ???????????? ???????? ???????????? ????????'
                )

            if ingredient['ingredient'] in available_ingredients:
                raise ValidationError(
                    '?????????????????????? ???? ???????????? ??????????????????????'
                )
            available_ingredients[ingredient['ingredient']] = True

        if data['cooking_time'] <= 0:
            raise ValidationError(
                '?????????? ?????????????? ???????????? ???????? ???????????? ????????'
            )

        return data

    @staticmethod
    def add_ingredients(instance, ingredients):
        for ingredient in ingredients:
            IngredientAmount.objects.get_or_create(
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
                recipe=instance
            )

    def create(self, validated_data):
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.add(*tags)
        self.add_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.clear()
            instance.tags.add(*tags)
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            IngredientAmount.objects.filter(recipe=instance).delete()
            self.add_ingredients(instance, ingredients)
        super().update(instance, validated_data)
        return instance

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        ]


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ['name', 'color', 'slug']

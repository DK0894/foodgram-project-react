from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Ingredient, IngredientRecipe, Tag, Recipe,
                              ShoppingCart, Favorite)
from users.serializers import UserSerializer, RecipeSubscribeSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AmountIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddAmountIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = AmountIngredientsSerializer(
        source='ingredient_recipes', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorired(self, obj):
        request = self.context['request']
        if request.user.is_anonymous or not request:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        if request.user.is_anonymous or not request:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = AmountIngredientsSerializer(
        source='ingredient_recipes', many=True
    )
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField(max_length=None, use_url=False)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')

    def validated_ingredients(self, value):
        ingredients_list = []
        for ingredient in value:
            ingredient_id = ingredient['ingredient']['id']
            some_ingredient = Ingredient.objects.filter(id=ingredient_id)
            if some_ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'В рецепте не может быть повторяющихся ингредиентов!'
                )
            # if some_ingredient['amount'] <= 1:
            #     raise serializers.ValidationError(
            #         'Количество ингредиентов не может быть меньше 1!'
            #     )
            if not some_ingredient.exists():
                raise serializers.ValidationError(
                    'Такого инредиенты нет в списке доступных!'
                )
            ingredients_list.append(some_ingredient)
        return value

    def validated_tags(self, value):
        tags_list = []
        if not value:
            raise serializers.ValidationError(
                'Рецепт должен иметь не меньше одного тега!'
            )
        for tag in value:
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Тэг не может повторяться!'
                )
            tags_list.append(tag)
        return value

    @staticmethod
    def add_ingredient(ingredients, recipe):
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    @staticmethod
    def add_tags(tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        author = self.context['request'].user
        print(validated_data)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        self.add_tags(tags, instance)
        self.add_ingredient(ingredients, instance)
        super().update(instance, validated_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context['request']
        context = {'request': request}
        return RecipeSubscribeSerializer(instance, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        # fields = ('id', 'name', 'image', 'cooking_time')
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context['request']
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Вы уже добавили этот рецепт в избранное!'
            )
        return data

    def to_representation(self, instance):
        request = self.context['request']
        context = {'request': request}
        return RecipeSubscribeSerializer(instance, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        # fields = ('id', 'name', 'image', 'cooking_time')
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context['request']
        context = {'request': request}
        return RecipeSubscribeSerializer(instance, context=context).data

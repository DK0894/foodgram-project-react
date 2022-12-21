from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.serializers import RecipeSubscribeSerializer, UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AmountIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddAmountIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')

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

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if not user.is_anonymous:
            return Favorite.objects.filter(
                user=user, recipe__id=obj.id
            ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(
                user=user, recipe__id=obj.id
            ).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = AddAmountIngredientsSerializer(
        source='ingredient_recipes', many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(max_length=None, use_url=False)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')

    def validate(self, attrs):
        if not attrs['ingredient_recipes']:
            raise serializers.ValidationError(
                'В рецепте не могут отсутствовать ингредиенты!'
            )
        print(attrs['ingredient_recipes'])

        ingredients_list = []
        for ingredient in attrs['ingredient_recipes']:
            print(ingredient['ingredient']['id'])
            ingredient_id = ingredient['ingredient']['id']
            some_ingredient = Ingredient.objects.filter(id=ingredient_id)
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    'В рецепте не может быть повторяющихся ингредиентов!'
                )
            if not some_ingredient.exists():
                raise serializers.ValidationError(
                    'Такого инредиенты нет в списке доступных!'
                )
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть больше нуля!'
                )
            ingredients_list.append(ingredient_id)

        tags_list = []
        if not attrs['tags']:
            raise serializers.ValidationError(
                'Рецепт должен иметь не меньше одного тега!'
            )
        for tag in attrs['tags']:
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Тэг не может повторяться!'
                )
            tags_list.append(tag)

        if int(attrs['cooking_time']) <= 0:
            raise serializers.ValidationError(
                'Время готовки должно быть больше 0!'
            )
        return attrs

    @staticmethod
    def add_ingredient(ingredients, recipe):
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @staticmethod
    def add_tags(tags, recipe):
        recipe.tags.set(tags, clear=True)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_recipes')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_recipes')
        IngredientRecipe.objects.filter(recipe=instance).delete()
        self.add_tags(tags, instance)
        self.add_ingredient(ingredients, instance)
        super().update(instance, validated_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context['request']
        context = {'request': request}
        return RecipeListSerializer(instance, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
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
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context['request']
        context = {'request': request}
        return RecipeSubscribeSerializer(instance, context=context).data

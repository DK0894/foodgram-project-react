from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, FavoriteSerializer,
                          IngredientsSerializer, RecipeListSerializer,
                          ShoppingCartSerializer, TagSerializer)
from .utils import pdf_create
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return CreateRecipeSerializer

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(
            total_ingredients=Sum('amount')
        )
        pdf = pdf_create(ingredients)
        return pdf


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs['recipes_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        Favorite.objects.create(user=request.user, recipe=recipe)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs['recipes_id']
        obj = get_object_or_404(
            Favorite, user__id=request.user.id, recipe__id=recipe_id
        )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs['recipes_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs['recipes_id']
        obj = get_object_or_404(
            ShoppingCart, user__id=request.user.id, recipe__id=recipe_id
        )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

from recipes.models import (Ingredient, Recipe, Tag, Favorite, ShoppingCart,
                            IngredientRecipe)
from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (TagSerializer, IngredientsSerializer,
                          RecipeListSerializer, CreateRecipeSerializer,
                          ShoppingCartSerializer, FavoriteSerializer)


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
        else:
            return CreateRecipeSerializer

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        cart_dict = {}
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_carts__user=request.user
        ).values('ingredient__name', 'ingredient__measurement_unit', 'amount')
        for item in ingredients:
            name = item['ingredient__name']
            if name not in cart_dict:
                cart_dict[name] = {
                    'measurement_unit': item['ingredient__measurement_unit'],
                    'amount': item['amount']
                }
            else:
                cart_dict[name]['amount'] += item['amount']
        pdfmetrics.registerFont(
            TTFont('TNR', 'times.ttf', 'UTF-8')
        )
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.pdf"'
        )
        page = canvas.Canvas(response, pagesize=A4)
        page.setFont('TNR', size=24)
        page.setTitle('Список покупок')
        page.drawString(200, 800, 'Список покупок')
        page.setFont('TNR', size=16)
        height = 750
        for i, (name, data) in enumerate(cart_dict.items(), 1):
            page.drawString(75, height, (f'{i}) {name} - {data["amount"]}'
                                         f'{data["measurement_unit"]}'))
            height -= 25
        page.showPage()
        page.save()
        return response


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

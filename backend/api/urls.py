from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, TagViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('recipes/<recipes_id>/favorite/', FavoriteViewSet.as_view(
        {'post': 'create', 'delete': 'delete'}), name='favorite'),
    path('recipes/<recipes_id>/shopping_cart/', ShoppingCartViewSet.as_view(
        {'post': 'create', 'delete': 'delete'}), name='cart'),
    path('', include(router.urls)),
]

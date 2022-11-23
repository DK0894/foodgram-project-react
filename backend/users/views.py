from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from djoser.views import UserViewSet as UVSet

from .models import User, Subscribe
from .serializers import UserSerializer, SubscribeSerializer


class UserViewSet(UVSet):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return User.objects.all()


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs.get('users_id')
        user = get_object_or_404(User, id=user_id)
        if user == request.user:
            return Response({'error': 'Вы пытаетесь подписаться на себя!'},
                            status=status.HTTP_400_BAD_REQUEST)
        if Subscribe.objects.filter(user=request.user,
                                    following=user).exists():
            return Response(
                {'error': 'Вы уже подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscribe.objects.create(user=request.user, following=user)
        return Response(
            self.serializer_class(user, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        author_id = self.kwargs.get('users_id')
        user_id = request.user.id
        subscribe = get_object_or_404(
            Subscribe, user__id=user_id, following__id=author_id
        )
        subscribe.delete()
        return Response(status.HTTP_204_NO_CONTENT)

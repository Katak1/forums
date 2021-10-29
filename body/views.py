from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Question, Answer, Comment, Rate, Favorite
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAuthorPermission
from .serializers import QuestionSerializer, AnswerSerializer, CommentSerializer, RateSerializer, FavoriteSerializer
from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters
from likes.mixins import LikedMixin


class PermissionMixin:
    def get_permissions(self):
        if self.action == 'create':
            permissions = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsAuthorPermission]
        else:
            permissions = []
        return [permission() for permission in permissions]


class QuestionViewSet(PermissionMixin, ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filter_backends = [
        filters.DjangoFilterBackend,
        rest_filters.SearchFilter
    ]
    filter_fields = ['title']
    search_fields = ['id']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        return context

class AnswerViewSet(PermissionMixin, LikedMixin ,ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        context['request'] = self.request
        return context

class CommentViewSet(PermissionMixin, ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class RateViewSet(ModelViewSet):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer

class FavoriteViewSet(ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.get_serializer_context().get('request').user
        queryset = Favorite.objects.filter(user=user)
        return  queryset



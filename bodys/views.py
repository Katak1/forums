from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Questions, Answers, Comments, Rates, Favorites
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


class QuestionsViewSet(PermissionMixin, ModelViewSet):
    queryset = Questions.objects.all()
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

class AnswersViewSet(PermissionMixin, LikedMixin ,ModelViewSet):
    queryset = Answers.objects.all()
    serializer_class = AnswerSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        context['request'] = self.request
        return context
        

class CommentsViewSet(PermissionMixin, ModelViewSet):
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer

class RatesViewSet(ModelViewSet):
    queryset = Rates.objects.all()
    serializer_class = RateSerializer

class FavoritesViewSet(ModelViewSet):
    queryset = Favorites.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.get_serializer_context().get('request').user
        queryset = Favorites.objects.filter(user=user)
        return  queryset


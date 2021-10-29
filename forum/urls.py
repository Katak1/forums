from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from body.views import QuestionViewSet, AnswerViewSet, CommentViewSet, FavoriteViewSet,RateViewSet
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls import url
from Pars.views import NewsViewSet


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register('question', QuestionViewSet)
router.register('answer', AnswerViewSet)
router.register('comment', CommentViewSet)
router.register('rate', RateViewSet)
router.register('favorite', FavoriteViewSet)
router.register('new', NewsViewSet)


urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/', include('account.urls')),
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0),
                      name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



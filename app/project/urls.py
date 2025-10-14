from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, re_path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin

from common.swagger import BothHttpAndHttpsSchemaGenerator


schema_view = get_schema_view(
   openapi.Info(
      title="Mas Developer API",
      default_version='v1',
      description="Aplicação Backend para servir de suporte para as aplicações da Central de Talentos",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="devmigueldev@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   generator_class=BothHttpAndHttpsSchemaGenerator,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [

    # Admin
    path('admin/', admin.site.urls),

    # LOGS
    path('logs/', include('logs.urls')),
    
    # Access
    path('access/', include('access.urls')),
]

# Swagger
urlpatterns += [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', login_required(schema_view.without_ui(cache_timeout=0), login_url="/admin"), name='schema-json'),
    re_path(r'^swagger/$', login_required(schema_view.with_ui('swagger', cache_timeout=0), login_url="/admin"), name='schema-json'),
    re_path(r'^redoc/$', login_required(schema_view.with_ui('redoc', cache_timeout=0), login_url="/admin"), name='schema-json'),   
]
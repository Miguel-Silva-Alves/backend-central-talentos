from drf_yasg.generators import OpenAPISchemaGenerator
from django.shortcuts import redirect
from django.urls import reverse


class SwaggerAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/swagger"):
            if not request.user.is_authenticated:
                return redirect(f"{reverse('admin:login')}?next={request.path}")
        return self.get_response(request)


class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema
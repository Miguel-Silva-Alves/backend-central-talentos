from django.urls import path, include
from access.views import UserViewSet
from common.router import getRouter


# Views
router = getRouter()

router.register(r'', UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
]

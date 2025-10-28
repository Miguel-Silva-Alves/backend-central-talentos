from django.urls import path, include
from rh.views import FileViewSet
from common.router import getRouter


# Views
router = getRouter()

router.register(r'file', FileViewSet)


urlpatterns = [
    path('', include(router.urls)),
]

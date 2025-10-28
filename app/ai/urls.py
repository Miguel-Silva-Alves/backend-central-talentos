from django.urls import path, include
from ai.views import QuerieViewSet
from common.router import getRouter


# Views
router = getRouter()

router.register(r'querie', QuerieViewSet)


urlpatterns = [
    path('', include(router.urls)),
]

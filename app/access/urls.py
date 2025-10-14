from django.urls import path, include
from access.views import RegisterUser
from common.router import getRouter


# Views
router = getRouter()

router.register(r'', RegisterUser)


urlpatterns = [
    path('', include(router.urls)),
]

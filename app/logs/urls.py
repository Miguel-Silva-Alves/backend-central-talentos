from django.urls import path, include

from common.router import getRouter

router = getRouter()


urlpatterns = [
    path('', include(router.urls)),

]

from django.urls import path, include
from company.views import CandidateViewSet
from common.router import getRouter


# Views
router = getRouter()

router.register(r'candidates', CandidateViewSet, basename='candidate')

urlpatterns = [
    path('', include(router.urls)),
]

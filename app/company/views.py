from company.models import Candidate
from company.serializer import CandidateSerializer
from rest_framework import viewsets

# Common
from common.token import TokenValidator
from common.response import ResponseDefault, CreatedRequest, BadRequest, NotFound, UnauthorizedRequest

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

    @TokenValidator.require_token
    def retrieve(self, request, *args, **kwargs):
        try:
            user = self.get_object()
        except Exception:
            return NotFound("candidate not found")
        serializer = self.get_serializer(user)
        return ResponseDefault("candidate retrieved", {"candidate": serializer.data})

    @TokenValidator.require_x_api_key
    def list(self, request, *args, **kwargs):
        candidates = self.get_queryset()
        serializer = self.get_serializer(candidates, many=True)
        return ResponseDefault("list of candidates", {"candidates": serializer.data})
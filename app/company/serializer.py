from rest_framework import serializers
from .models import Candidate


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = [
            "id", "name", "email", "birth_date", "current_position",
            "years_experience", "location", "phone"
        ]

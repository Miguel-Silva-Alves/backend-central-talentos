# company/serializer.py

from rest_framework import serializers
from rh.models import File
from .models import Candidate, FileCandidate


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"
        ref_name = "CompanyFile"


class FileCandidateSerializer(serializers.ModelSerializer):
    file = FileSerializer()

    class Meta:
        model = FileCandidate
        fields = ["id", "file", "uploaded_at"]


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = [
            "id",
            "name",
            "email",
            "birth_date",
            "current_position",
            "years_experience",
            "location",
            "phone",
            "files",
            "profile_resume"
        ]
        read_only_fields = ["files"]


from rest_framework import serializers
from rh.models import File


class FileSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = File
        fields = [
            "pk",
            "name",
            "size_mb",
            "processed",
            "date_upload",
        ]

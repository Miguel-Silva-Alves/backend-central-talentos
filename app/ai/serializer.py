from rest_framework import serializers
from ai.models import Queries

class QuerieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queries
        fields = '__all__'
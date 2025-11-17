from rest_framework import serializers
from ai.models import Queries

class QuerieSerializer(serializers.ModelSerializer):
    prompt = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Queries
        fields = ['id', 'ask', 'prompt', 'answer', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def validate(self, attrs):
        # Se tiver prompt, copia para ask
        if 'prompt' in attrs and not attrs.get('ask'):
            attrs['ask'] = attrs['prompt']
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user

        # remove 'prompt' antes de criar
        validated_data.pop('prompt', None)
        return super().create(validated_data)

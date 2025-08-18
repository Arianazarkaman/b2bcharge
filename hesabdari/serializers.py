from rest_framework import serializers
from hesabdari.models import EtebarTaghir, HesabEntry

class EtebarTaghirSerializer(serializers.ModelSerializer):
    foroshande_name = serializers.CharField(source='foroshande.name', read_only=True)

    class Meta:
        model = EtebarTaghir
        fields = ['id', 'foroshande', 'foroshande_name', 'amount', 'status', 'idempotency_key', 'created_at', 'approved_at']


class HesabEntrySerializer(serializers.ModelSerializer):
    foroshande_name = serializers.CharField(source='foroshande.name', read_only=True)

    class Meta:
        model = HesabEntry
        fields = ['id', 'foroshande', 'foroshande_name', 'kind', 'amount', 'ref_type', 'ref_id', 'created_at']

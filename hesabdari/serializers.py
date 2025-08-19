from rest_framework import serializers
from .models import HesabEntry

class HesabEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = HesabEntry
        fields = [
            "id",
            "foroshande",
            "kind",
            "amount",
            "status",
            "ref_type",
            "ref_id",
            "created_at",
            "approved_at",
        ]
        read_only_fields = ["id", "status", "created_at", "approved_at"]



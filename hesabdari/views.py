from rest_framework import generics, status
from rest_framework.response import Response
from django.utils import timezone

from hesabdari.models import EtebarTaghir, HesabEntry
from hesabdari.serializers import EtebarTaghirSerializer, HesabEntrySerializer
from hesabdari.services import approve_credit

# -------------------------
# Accounting / Hesabdari Views
# -------------------------

class ApproveCreditView(generics.GenericAPIView):
    serializer_class = EtebarTaghirSerializer

    def post(self, request):
        adjustment_id = request.data.get("adjustment_id")
        if not adjustment_id:
            return Response({"error": "adjustment_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            adj = approve_credit(adjustment_id)
            serializer = self.get_serializer(adj)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class HesabEntryListView(generics.ListAPIView):
    serializer_class = HesabEntrySerializer

    def get_queryset(self):
        foroshande_id = self.kwargs["foroshande_id"]
        return HesabEntry.objects.filter(foroshande_id=foroshande_id).order_by("created_at")


class EtebarTaghirListView(generics.ListAPIView):
    serializer_class = EtebarTaghirSerializer

    def get_queryset(self):
        foroshande_id = self.kwargs["foroshande_id"]
        return EtebarTaghir.objects.filter(foroshande_id=foroshande_id).order_by("created_at")

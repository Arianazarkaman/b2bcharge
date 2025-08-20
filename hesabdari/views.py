from rest_framework import generics, status
from rest_framework.response import Response
from django.utils import timezone
from hesabdari.models import HesabEntry
from hesabdari.serializers import HesabEntrySerializer
from hesabdari.services import approve_entry  
from rest_framework.permissions import IsAdminUser


class ApproveHesabEntryView(generics.GenericAPIView):
    serializer_class = HesabEntrySerializer
    permission_classes = [IsAdminUser]


    def post(self, request):
        entry_id = request.data.get("entry_id")
        if not entry_id:
            return Response({"error": "entry_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        admin_user = request.user  

        try:
            approved_entry = approve_entry(entry_id, admin_user)
            serializer = self.get_serializer(approved_entry)
            return Response(serializer.data)
        except HesabEntry.DoesNotExist:
            return Response({"error": "Entry not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class HesabEntryListView(generics.ListAPIView):
    serializer_class = HesabEntrySerializer

    def get_queryset(self):
        foroshande_id = self.kwargs["foroshande_id"]
        return HesabEntry.objects.filter(foroshande_id=foroshande_id).order_by("created_at")

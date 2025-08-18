from rest_framework import generics, status
from rest_framework.response import Response
from decimal import Decimal

from core.models import Foroshande, PhoneNumber, Charge
from core.serializers import PhoneNumberSerializer, ChargeSerializer, ForoshandeBalanceSerializer
from core.services import charge_phone

# -------------------------
# Core / Seller Views
# -------------------------

class ChargePhoneView(generics.GenericAPIView):
    serializer_class = ChargeSerializer

    def post(self, request):
        foroshande_id = request.data.get("foroshande_id")
        phone_id = request.data.get("phone_id")
        amount = request.data.get("amount")
        request_id = request.data.get("request_id")

        if not all([foroshande_id, phone_id, amount, request_id]):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            charge = charge_phone(foroshande_id, phone_id, amount, request_id)
            serializer = self.get_serializer(charge)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PhoneNumberListView(generics.ListAPIView):
    serializer_class = PhoneNumberSerializer
    queryset = PhoneNumber.objects.all()


class ForoshandeBalanceView(generics.RetrieveAPIView):
    serializer_class = ForoshandeBalanceSerializer
    lookup_field = "id"
    queryset = Foroshande.objects.all()

from rest_framework import generics, status
from rest_framework.response import Response
from core.models import Foroshande, PhoneNumber, Charge
from core.serializers import PhoneNumberSerializer, ChargeSerializer, ForoshandeBalanceSerializer, CreditAddRequestSerializer, ForoshandeCreateSerializer
from core.services import charge_phone
from hesabdari.models import HesabEntry
from django.db import transaction
from django.utils import timezone


class ChargePhoneView(generics.GenericAPIView):
    serializer_class = ChargeSerializer

    @transaction.atomic
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


class ChargeListView(generics.ListAPIView):
    serializer_class = ChargeSerializer

    def get_queryset(self):
        foroshande_id = self.kwargs.get("foroshande_id")
        return Charge.objects.filter(foroshande_id=foroshande_id).order_by("-created_at")



class CreditAddRequestView(generics.GenericAPIView):
    """
    Foroshande requests to add credit.
    Creates a pending HesabEntry (MONTAZER) with kind=BES.
    Approval happens later via existing HesabEntry approval view.
    """
    serializer_class = CreditAddRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        foroshande_id = serializer.validated_data["foroshande_id"]
        amount = serializer.validated_data["amount"]

        # Create a pending HesabEntry
        entry = HesabEntry.objects.create(
            foroshande_id=foroshande_id,
            kind=HesabEntry.BES,  # credit
            amount=amount,
            ref_type="CREDIT",
            ref_id=f"CREDIT-{foroshande_id}-{int(timezone.now().timestamp())}"
        )

        return Response({
            "success": True,
            "entry_id": entry.id,
            "status": entry.status,
            "amount": entry.amount
        }, status=status.HTTP_201_CREATED)
    

class ForoshandeCreateView(generics.GenericAPIView):
    serializer_class = ForoshandeCreateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        foroshande = serializer.save()
        return Response({
            "id": foroshande.id,
            "name": foroshande.name,
            "balance": foroshande.balance,
            "user_id": foroshande.user.id
        }, status=status.HTTP_201_CREATED)
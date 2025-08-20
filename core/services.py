from django.db import transaction
from decimal import Decimal
from .models import Charge, PhoneNumber, Foroshande
from hesabdari.models import HesabEntry
from django.utils import timezone

def charge_phone(foroshande_id, phone_id, amount, request_id):
    """
    Charge a phone number for a Foroshande.
    Fully thread-safe and prevents negative balances under high concurrency.
    Records a debit entry (BED) automatically in HesabEntry.
    """

    amount = Decimal(amount)

    #  Lock Foroshande row to prevent race conditions
    foroshande = Foroshande.objects.select_for_update().get(id=foroshande_id)
    phone = PhoneNumber.objects.get(id=phone_id)

    #  Create Charge immediately for idempotency, even if insufficient balance
    charge, created = Charge.objects.get_or_create(
        foroshande_id=foroshande_id,
        request_id=request_id,
        defaults={"phone": phone, "amount": amount, "status": Charge.NAMOVAFAGH},
    )
    if not created:
        return charge  # already processed

    # Check balance after Charge creation
    if not foroshande.can_deduct(amount):
        
        charge.save(update_fields=["status"])
        raise ValueError(f"Foroshande {foroshande.id} has insufficient balance")

    #chek the balance to see if it is able to sell charge
    with transaction.atomic():
        # lock again to prevent race condition
        foroshande = Foroshande.objects.select_for_update().get(id=foroshande_id)

        foroshande.balance -= amount
        foroshande.save(update_fields=["balance"])

        HesabEntry.objects.create(
            foroshande=foroshande,
            kind=HesabEntry.BED,
            amount=amount,
            status=HesabEntry.TAIED,
            ref_type="CHARGE",
            ref_id=request_id,
            approved_at=timezone.now(),
            approved_by=None
        )

        # Update charge status to MOVAFAGH
        charge.status = Charge.MOVAFAGH
        charge.save(update_fields=["status"])

    return charge

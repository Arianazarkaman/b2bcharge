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

    with transaction.atomic():
        # Lock Foroshande row to prevent race conditions
        foroshande = Foroshande.objects.select_for_update().get(id=foroshande_id)
        phone = PhoneNumber.objects.get(id=phone_id)

        # Ensure idempotency: do not charge twice for the same request_id
        charge, created = Charge.objects.get_or_create(
            foroshande_id=foroshande_id,
            request_id=request_id,
            defaults={"phone": phone, "amount": amount, "status": Charge.NAMOVAFAGH},
        )
        if not created:
            return charge  # already processed

        # Check balance
        if not foroshande.can_deduct(amount):
            charge.status = Charge.NAMOVAFAGH
            charge.save(update_fields=["status"])
            raise ValueError(f"Foroshande {foroshande.id} has insufficient balance")

        # Deduct balance
        foroshande.balance -= amount
        foroshande.save(update_fields=["balance"])

        # Record a debit (BED) in HesabEntry automatically
        HesabEntry.objects.create(
            foroshande=foroshande,
            kind=HesabEntry.BED,
            amount=amount,
            status=HesabEntry.TAIED,  # automatically approved
            ref_type="CHARGE",
            ref_id=request_id,
            approved_at=timezone.now(),
            approved_by=None  # no admin for automatic debit
        )

        # Update charge status
        charge.status = Charge.MOVAFAGH
        charge.save(update_fields=["status"])

        return charge

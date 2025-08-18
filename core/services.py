# from django.db import transaction, models
# from decimal import Decimal
# from hesabdari.models import HesabEntry
# from .models import Charge, PhoneNumber, Foroshande


# def charge_phone(foroshande_id, phone_id, amount, request_id):
#     amount = Decimal(amount)

#     with transaction.atomic():
#         phone = PhoneNumber.objects.get(id=phone_id)

#         charge, created = Charge.objects.get_or_create(
#             foroshande_id=foroshande_id,
#             request_id=request_id,
#             defaults={"phone": phone, "amount": amount, "status": Charge.NAMOVAFAGH},
#         )
#         if not created:
#             return charge  # already did this process return the existing charge

#         # checking the balance 
#         total_bes = HesabEntry.objects.filter(foroshande_id=foroshande_id, kind=HesabEntry.BES).aggregate(total=models.Sum("amount"))["total"] or 0
#         total_bed = HesabEntry.objects.filter(foroshande_id=foroshande_id, kind=HesabEntry.BED).aggregate(total=models.Sum("amount"))["total"] or 0
#         balance = total_bes - total_bed

#         if balance < amount:
#             charge.status = Charge.NAMOVAFAGH
#             charge.save(update_fields=["status"])
#             raise ValueError("Insufficient balance")

#         # add ledger entry
#         HesabEntry.objects.create(
#             foroshande_id=foroshande_id,
#             kind=HesabEntry.BED,
#             amount=amount,
#             ref_type="SHARGE",
#             ref_id=request_id,
#         )

#         charge.status = Charge.MOVAFAGH
#         charge.save(update_fields=["status"])
#         return charge


from django.db import transaction, models
from decimal import Decimal
from .models import Charge, PhoneNumber, Foroshande
from hesabdari.models import HesabEntry

def charge_phone(foroshande_id, phone_id, amount, request_id):
    """
    Charge a phone number for a Foroshande.
    Fully thread-safe and prevents negative balances under high concurrency.
    """
    amount = Decimal(amount)

    with transaction.atomic():
        # Lock Foroshande row
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

        # Lock all related ledger entries to prevent race conditions
        HesabEntry.objects.select_for_update().filter(foroshande_id=foroshande_id)

        # Calculate current balance safely
        if foroshande.balance < amount:
            charge.status = Charge.NAMOVAFAGH
            charge.save(update_fields=["status"])
            raise ValueError(f"Foroshande {foroshande.id} has insufficient balance")

        # Deduct balance
        foroshande.balance -= amount
        foroshande.save(update_fields=["balance"])

        # Record the debit in the ledger
        HesabEntry.objects.create(
            foroshande_id=foroshande_id,
            kind=HesabEntry.BED,
            amount=amount,
            ref_type="CHARGE",
            ref_id=request_id,
        )

        # Update charge status
        charge.status = Charge.MOVAFAGH
        charge.save(update_fields=["status"])
        return charge


def approve_credit(foroshande_id, amount, request_id):
    """
    Approve a credit increase for a Foroshande. Thread-safe and idempotent.
    """
    amount = Decimal(amount)

    with transaction.atomic():
        foroshande = Foroshande.objects.select_for_update().get(id=foroshande_id)

        # Check for existing record to prevent double-adding
        existing = HesabEntry.objects.filter(foroshande_id=foroshande_id, ref_type="CREDIT", ref_id=request_id).first()
        if existing:
            return existing  # already processed

        # Create credit ledger entry
        entry = HesabEntry.objects.create(
            foroshande_id=foroshande_id,
            kind=HesabEntry.BES,
            amount=amount,
            ref_type="CREDIT",
            ref_id=request_id,
        )

        # Update Foroshande balance
        foroshande.balance += amount
        foroshande.save(update_fields=["balance"])

        return entry

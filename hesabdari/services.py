from django.db import transaction
from django.utils import timezone
from django.db.models import Sum
from .models import HesabEntry
from core.models import Foroshande

def approve_entry(entry_id, admin_user):
    """
    Approve a HesabEntry safely.
    Updates Foroshande balance, prevents negative balance,
    and uses aggregation to calculate current balance.
    """
    with transaction.atomic():
        entry = HesabEntry.objects.select_for_update().get(id=entry_id)
        if entry.status == HesabEntry.TAIED:
            return entry  # already approved

        f = Foroshande.objects.select_for_update().get(id=entry.foroshande_id)

        # Calculate current balance using aggregation
        total_bes = HesabEntry.objects.filter(foroshande=f, kind=HesabEntry.BES, status=HesabEntry.TAIED).aggregate(total=Sum("amount"))["total"] or 0
        total_bed = HesabEntry.objects.filter(foroshande=f, kind=HesabEntry.BED, status=HesabEntry.TAIED).aggregate(total=Sum("amount"))["total"] or 0
        current_balance = total_bes - total_bed

        # Determine new balance after this entry
        new_balance = current_balance + entry.amount if entry.kind == HesabEntry.BES else current_balance - entry.amount

        if new_balance < 0:
            entry.status = HesabEntry.RAD
            entry.save(update_fields=["status"])
            raise ValueError("Cannot approve entry: would make balance negative")

        # Update Foroshande balance
        f.balance = new_balance
        f.save(update_fields=["balance"])

        # Approve the entry
        entry.status = HesabEntry.TAIED
        entry.approved_at = timezone.now()
        entry.approved_by = admin_user
        entry.save(update_fields=["status", "approved_at", "approved_by"])

        return entry

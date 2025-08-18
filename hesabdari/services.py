from django.db import transaction
from django.utils import timezone
from .models import EtebarTaghir, HesabEntry
from django.db.models import Sum

def approve_credit(adjustment_id):
    with transaction.atomic():
        adj = EtebarTaghir.objects.select_for_update().get(id=adjustment_id)

        # if it already has been accepted don't double process it just return it

        if adj.status == EtebarTaghir.TAIED:
            return adj

        foroshande = adj.foroshande
        total_bes = HesabEntry.objects.filter(foroshande=foroshande, kind=HesabEntry.BES).aggregate(total=Sum("amount"))["total"] or 0
        total_bed = HesabEntry.objects.filter(foroshande=foroshande, kind=HesabEntry.BED).aggregate(total=Sum("amount"))["total"] or 0

        new_balance = total_bes - total_bed + adj.amount
        if new_balance < 0:
            raise ValueError("Cannot approve credit: would make balance negative")
        
        # normalli we add to an entry but we made this for the case if there is a decrease of budget in an entry

        if adj.amount > 0:
            entry_kind = HesabEntry.BES
        else:
            entry_kind = HesabEntry.BED

        # add the amoutn to this entry 
        HesabEntry.objects.create(
            foroshande=foroshande,
            kind=entry_kind,
            amount=abs(adj.amount),
            ref_type="ETEBAR_TAGHIR",
            ref_id=str(adj.id),
        )

        adj.status = EtebarTaghir.TAIED
        adj.approved_at = timezone.now()
        adj.save(update_fields=["status", "approved_at"])
        return adj


from django.db import models
from django.utils import timezone
from core.models import Foroshande

class EtebarTaghir(models.Model):
    MONTAZER = 'MONTAZER'
    TAIED = 'TAIED'
    RAD = 'RAD'
    STATUS_CHOICES = [
        (MONTAZER, 'Montazer'),
        (TAIED, 'Taied Shodeh'),
        (RAD, 'Rad Shodeh'),
    ]

    foroshande = models.ForeignKey(
        Foroshande, 
        on_delete=models.CASCADE, 
        related_name="etebar_taghirat",
        db_index=True  # indexed for faster lookups
    )
    amount = models.DecimalField(max_digits=18, decimal_places=0)  # can be + or -
    idempotency_key = models.CharField(max_length=64, unique=True) # if an api is called twice with this key one of them will be considered
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=MONTAZER)
    created_at = models.DateTimeField(default=timezone.now)
    approved_at = models.DateTimeField(null=True, blank=True)


class HesabEntry(models.Model):
    BES = 'BES'  # credit
    BED = 'BED'  # debit
    KIND_CHOICES = [(BES, 'Bes'), (BED, 'Bed')]

    foroshande = models.ForeignKey(
        Foroshande, 
        on_delete=models.CASCADE, 
        related_name="hesab_entries",
        db_index=True  # indexed for faster lookups
    )
    kind = models.CharField(max_length=3, choices=KIND_CHOICES)
    amount = models.DecimalField(max_digits=18, decimal_places=0)  # always > 0
    ref_type = models.CharField(max_length=50)  # e.g., ETEBAR_TAGHIR, SHARGE
    ref_id = models.CharField(max_length=64)   # unique reference id
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="amount_gt_0"),
            models.UniqueConstraint(fields=['foroshande', 'ref_type', 'ref_id'], name="unique_hesab_ref"),
        ]

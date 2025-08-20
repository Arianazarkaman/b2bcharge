from django.contrib.auth.models import User
from core.models import Foroshande
from hesabdari.models import HesabEntry
from hesabdari.services import approve_entry
from decimal import Decimal

admin = User.objects.get(username="admin")

for i in range(1, 11):
    user, _ = User.objects.get_or_create(username=f"seller{i}")
    f, _ = Foroshande.objects.get_or_create(user=user, defaults={"name": f"Seller {i}", "balance": 0})
    entry = HesabEntry.objects.create(
        foroshande=f,
        kind=HesabEntry.BES,
        amount=Decimal("1000000"),
        ref_type="CREDIT",
        ref_id=f"CREDIT-{i}",
        status=HesabEntry.MONTAZER,
    )
    approve_entry(entry.id, admin)
    f.refresh_from_db()
    print(f"Seller {i} balance → {f.balance}")

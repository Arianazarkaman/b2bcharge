from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from hesabdari.models import HesabEntry
from hesabdari.services import approve_entry
from core.models import Foroshande


class HesabdariTests(TestCase):
    def test_approve_entry_negative_balance_prevented(self):
        user = User.objects.create(username="seller2")
        f = Foroshande.objects.create(user=user, name="Seller 2", balance=0)

        entry = HesabEntry.objects.create(
            foroshande=f,
            kind=HesabEntry.BED,
            amount=Decimal("1000"),
            ref_type="CHARGE",
            ref_id="NEG-1",
            status=HesabEntry.MONTAZER,
        )

        admin = User.objects.create(username="admin2")

        result = approve_entry(entry.id, admin)  # no exception

        result.refresh_from_db()
        f.refresh_from_db()
        self.assertEqual(result.status, HesabEntry.RAD)
        self.assertEqual(f.balance, 0)

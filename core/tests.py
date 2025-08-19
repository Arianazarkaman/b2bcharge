from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from core.models import Foroshande, PhoneNumber, Charge
from hesabdari.models import HesabEntry
from core.services import charge_phone
from hesabdari.services import approve_entry


class CoreTests(TestCase):

    def setup_foroshande(self):
        user = User.objects.create(username="seller1")
        f = Foroshande.objects.create(user=user, name="Seller 1", balance=0)
        return f

    def test_credit_request_and_approval(self):
        f = self.setup_foroshande()
        entry = HesabEntry.objects.create(
            foroshande=f,
            kind=HesabEntry.BES,
            amount=Decimal("1000"),
            ref_type="CREDIT",
            ref_id="CREDIT-1",
            status=HesabEntry.MONTAZER,
        )
        admin = User.objects.create(username="admin")
        approved = approve_entry(entry.id, admin)

        self.assertEqual(approved.status, HesabEntry.TAIED)
        f.refresh_from_db()
        self.assertEqual(f.balance, Decimal("1000"))

    def test_charge_phone_success_and_entry(self):
        f = self.setup_foroshande()
        f.balance = Decimal("5000")
        f.save()
        phone = PhoneNumber.objects.create(mobile_number=12345)
        charge = charge_phone(f.id, phone.id, Decimal("2000"), "REQ-1")
        f.refresh_from_db()

        self.assertEqual(charge.status, Charge.MOVAFAGH)
        self.assertEqual(f.balance, Decimal("3000"))

        entry = HesabEntry.objects.get(ref_id="REQ-1")
        self.assertEqual(entry.kind, HesabEntry.BED)
        self.assertEqual(entry.amount, Decimal("2000"))
        self.assertEqual(entry.status, HesabEntry.TAIED)

    def test_charge_phone_insufficient_balance(self):
        f = self.setup_foroshande()
        phone = PhoneNumber.objects.create(mobile_number=67890)
        with self.assertRaises(ValueError):
            charge_phone(f.id, phone.id, Decimal("1000"), "REQ-2")
        f.refresh_from_db()
        self.assertEqual(f.balance, 0)
        self.assertTrue(Charge.objects.filter(request_id="REQ-2").exists())

    def test_charge_phone_idempotency(self):
        f = self.setup_foroshande()
        f.balance = Decimal("5000")
        f.save()
        phone = PhoneNumber.objects.create(mobile_number=99999)

        c1 = charge_phone(f.id, phone.id, Decimal("1000"), "REQ-3")
        c2 = charge_phone(f.id, phone.id, Decimal("1000"), "REQ-3")

        self.assertEqual(c1.id, c2.id)
        f.refresh_from_db()
        self.assertEqual(f.balance, Decimal("4000"))

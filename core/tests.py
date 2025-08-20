from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from core.models import Foroshande, PhoneNumber
from core.services import charge_phone
from hesabdari.models import HesabEntry
from hesabdari.services import approve_entry


class HesabdarTest(TestCase):

    def test_foroshande_credit_and_multiple_charges(self):
        # Create admin and foroshande


        admin = User.objects.create(username="admin")
        user = User.objects.create(username="seller1")

        f = Foroshande.objects.create(user=user, name="Seller 1", balance=0)
        print(f"Initial balance: {f.balance}")

        # first 1: Add credit request and approve
        credit_entry = HesabEntry.objects.create(
            foroshande=f,
            kind=HesabEntry.BES,
            amount=Decimal("1000000"),  # 1M
            ref_type="CREDIT",
            ref_id="CREDIT-1",
            status=HesabEntry.MONTAZER,
        )
        print(f"Created credit entry: {credit_entry.ref_id}, amount: {credit_entry.amount}")

        approved_entry = approve_entry(credit_entry.id, admin)
        print(f"Approved entry: {approved_entry.ref_id}, status: {approved_entry.status}")

        f.refresh_from_db()
        print(f"Balance after approval: {f.balance}")
        self.assertEqual(f.balance, Decimal("1000000"))

        # second 2: Create 60 phone numbers and charge 5000 each
        for i in range(60):
            phone = PhoneNumber.objects.create(mobile_number=100000 + i)
            charge = charge_phone(f.id, phone.id, Decimal("5000"), f"REQ-{i+1}")
            print(f"Charged phone {phone.mobile_number}: {charge.amount} => new balance: {f.balance}")
            f.refresh_from_db()

        # thirdd 3: Check final balance
        f.refresh_from_db()
        expected_balance = Decimal("1000000") - (60 * Decimal("5000"))
        print(f"Expected final balance: {expected_balance}, actual: {f.balance}")
        self.assertEqual(f.balance, expected_balance)

        # fourth 4: Check HesabEntry records
        print("Checking HesabEntry records counts...")
        bed_count = HesabEntry.objects.filter(foroshande=f, kind=HesabEntry.BED, status=HesabEntry.TAIED).count()
        bes_count = HesabEntry.objects.filter(foroshande=f, kind=HesabEntry.BES, status=HesabEntry.TAIED).count()
        print(f"BED entries: {bed_count}, BES entries: {bes_count}")

        self.assertEqual(bed_count, 60)
        self.assertEqual(bes_count, 1)


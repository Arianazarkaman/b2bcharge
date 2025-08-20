from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from core.models import Foroshande, PhoneNumber
from core.services import charge_phone
from hesabdari.models import HesabEntry
from hesabdari.services import approve_entry


class HesabdariLargeIntegrationTest(TestCase):

    def test_multiple_sellers_credit_and_charges(self):
        admin = User.objects.create(username="admin")

        #Create 2 sellers
        seller_users = [User.objects.create(username=f"seller{i+1}") for i in range(2)]
        sellers = [
            Foroshande.objects.create(user=u, name=f"Seller {i+1}", balance=0)
            for i, u in enumerate(seller_users)
        ]
        for s in sellers:
            print(f"Created seller {s.name} with initial balance {s.balance}")

        # 2: Add 10 credit increases total (5 each seller for balance symmetry)
        for i, s in enumerate(sellers):
            for j in range(5):
                credit_entry = HesabEntry.objects.create(
                    foroshande=s,
                    kind=HesabEntry.BES,
                    amount=Decimal("500000"),  
                    ref_type="CREDIT",
                    ref_id=f"S{s.id}-CREDIT-{j+1}",
                    status=HesabEntry.MONTAZER,
                )
                print(f"Created credit entry {credit_entry.ref_id} for {s.name}")
                approve_entry(credit_entry.id, admin)

            s.refresh_from_db()
            print(f"Balance after credits for {s.name}: {s.balance}")

        # 3: Perform 1000 charges total (alternate sellers)
        for i in range(1000):
            seller = sellers[i % 2]
            phone = PhoneNumber.objects.create(mobile_number=300000 + i)
            charge = charge_phone(seller.id, phone.id, Decimal("1000"), f"REQ-{i+1}")
            seller.refresh_from_db()
            print(f"Charge {i+1}: Seller {seller.name} charged {charge.amount} -> balance {seller.balance}")

        # 4: Validate balances vs HesabEntry records
        for s in sellers:
            s.refresh_from_db()
            bes_sum = HesabEntry.objects.filter(foroshande=s, kind=HesabEntry.BES, status=HesabEntry.TAIED).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")
            bed_sum = HesabEntry.objects.filter(foroshande=s, kind=HesabEntry.BED, status=HesabEntry.TAIED).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

            print(f"Final check {s.name}: balance={s.balance}, BES total={bes_sum}, BED total={bed_sum}")
            self.assertEqual(s.balance, bes_sum - bed_sum)

        # 5: Check total HesabEntry counts
        total_bes = HesabEntry.objects.filter(kind=HesabEntry.BES, status=HesabEntry.TAIED).count()
        total_bed = HesabEntry.objects.filter(kind=HesabEntry.BED, status=HesabEntry.TAIED).count()
        print(f"Total BES entries: {total_bes}, Total BED entries: {total_bed}")

        self.assertEqual(total_bes, 10)
        self.assertEqual(total_bed, 1000)

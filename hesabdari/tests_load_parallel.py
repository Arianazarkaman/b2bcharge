from django.test import TransactionTestCase
from django.contrib.auth.models import User
from core.models import Foroshande, PhoneNumber, Charge
from core.services import charge_phone, approve_credit
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import uuid

def foroshande_balance(foroshande):
    """
    Compute balance directly from Foroshande.balance.
    """
    foroshande.refresh_from_db()
    return foroshande.balance

class ParallelLoadTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        # Create Users
        self.user1 = User.objects.create(username="seller1")
        self.user2 = User.objects.create(username="seller2")

        # Create Foroshande linked to users
        self.seller1 = Foroshande.objects.create(user=self.user1, name="Seller1")
        self.seller2 = Foroshande.objects.create(user=self.user2, name="Seller2")

        # Create Phones
        self.phone1 = PhoneNumber.objects.create(mobile_number="989123456789")
        self.phone2 = PhoneNumber.objects.create(mobile_number="989987654321")

        # Approve large initial credits using thread-safe service
        # Ensure enough balance for all 5000*1000/2 recharges per seller
        total_needed = 5000 * 500  # 500 threads per seller
        approve_credit(self.seller1.id, total_needed, str(uuid.uuid4()))
        approve_credit(self.seller2.id, total_needed, str(uuid.uuid4()))

    def test_parallel_recharges(self):
        total_attempts = 1000
        successes = 0
        failures = 0
        lock = Lock()

        def do_recharge(seller, phone):
            nonlocal successes, failures
            req_id = str(uuid.uuid4())
            try:
                # Use thread-safe service
                charge_phone(seller.id, phone.id, 5000, req_id)
                with lock:
                    successes += 1
            except Exception:
                with lock:
                    failures += 1

        # Run threads in parallel
        with ThreadPoolExecutor(max_workers=50) as executor:
            for i in range(total_attempts // 2):
                executor.submit(do_recharge, self.seller1, self.phone1)
                executor.submit(do_recharge, self.seller2, self.phone2)

        # Refresh final balances
        seller1_sum = foroshande_balance(self.seller1)
        seller2_sum = foroshande_balance(self.seller2)

        # Print results
        print("\n=== PARALLEL LOAD TEST RESULTS ===")
        print(f"Total attempted recharges: {total_attempts}")
        print(f"Total successes: {successes}, failures: {failures}")
        print(f"Seller1 final balance: {seller1_sum}")
        print(f"Seller2 final balance: {seller2_sum}")

        # Assertions: balances should never be negative
        self.assertGreaterEqual(seller1_sum, 0)
        self.assertGreaterEqual(seller2_sum, 0)

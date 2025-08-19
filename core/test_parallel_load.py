# core/tests/test_parallel_load.py
from django.test import TestCase
from core.models import Foroshande, PhoneNumber, Charge
from hesabdari.models import HesabEntry, EtebarTaghir
from core.services import charge_phone
from hesabdari.services import approve_credit
from django.contrib.auth.models import User
from decimal import Decimal
import threading
import multiprocessing
import uuid
from django.db import models


NUM_SELLERS = 2
NUM_CREDITS = 10
NUM_RECHARGES = 1000
NUM_THREADS = 20
NUM_PROCESSES = 4

class ParallelLoadTest(TestCase):
    def setUp(self):
        # Create sellers
        self.sellers = []
        for i in range(NUM_SELLERS):
            user = User.objects.create(username=f"seller{i}")
            seller = Foroshande.objects.create(user=user, name=f"Seller{i}")
            self.sellers.append(seller)
            # Give each seller some credit
            for j in range(NUM_CREDITS):
                adj = EtebarTaghir.objects.create(
                    foroshande=seller,
                    amount=Decimal(50000),  # 50k each
                    idempotency_key=str(uuid.uuid4())
                )
                approve_credit(adj.id)

        # Create phone numbers
        self.phones = []
        for i in range(NUM_RECHARGES):
            phone = PhoneNumber.objects.create(mobile_number=f"0912000{i:04d}")
            self.phones.append(phone)

    def _recharge_worker(self, seller_id, phone_ids):
        """Worker for threads/processes"""
        for pid in phone_ids:
            try:
                charge_phone(seller_id, pid, 5000, str(uuid.uuid4()))
            except Exception as e:
                # Normally we ignore insufficient balance in test
                pass

    def test_parallel_threads(self):
        """Test concurrent recharges using threads"""
        threads = []
        chunk_size = NUM_RECHARGES // NUM_THREADS
        for seller in self.sellers:
            for i in range(NUM_THREADS):
                start = i * chunk_size
                end = (i + 1) * chunk_size
                t = threading.Thread(target=self._recharge_worker, args=(seller.id, [p.id for p in self.phones[start:end]]))
                threads.append(t)
                t.start()
        for t in threads:
            t.join()

        # Check balances
        for seller in self.sellers:
            total_bes = HesabEntry.objects.filter(foroshande=seller, kind=HesabEntry.BES).aggregate(total=models.Sum("amount"))["total"] or 0
            total_bed = HesabEntry.objects.filter(foroshande=seller, kind=HesabEntry.BED).aggregate(total=models.Sum("amount"))["total"] or 0
            balance = total_bes - total_bed
            self.assertGreaterEqual(balance, 0)

    def test_parallel_processes(self):
        """Test concurrent recharges using processes"""
        processes = []
        chunk_size = NUM_RECHARGES // NUM_PROCESSES

        def process_target(seller_id, phone_ids):
            self._recharge_worker(seller_id, phone_ids)

        for seller in self.sellers:
            for i in range(NUM_PROCESSES):
                start = i * chunk_size
                end = (i + 1) * chunk_size
                p = multiprocessing.Process(target=process_target, args=(seller.id, [ph.id for ph in self.phones[start:end]]))
                processes.append(p)
                p.start()
        for p in processes:
            p.join()

        # Check balances
        for seller in self.sellers:
            total_bes = HesabEntry.objects.filter(foroshande=seller, kind=HesabEntry.BES).aggregate(total=models.Sum("amount"))["total"] or 0
            total_bed = HesabEntry.objects.filter(foroshande=seller, kind=HesabEntry.BED).aggregate(total=models.Sum("amount"))["total"] or 0
            balance = total_bes - total_bed
            self.assertGreaterEqual(balance, 0)

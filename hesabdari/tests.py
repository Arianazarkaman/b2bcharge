from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Foroshande
from hesabdari.models import EtebarTaghir, HesabEntry
from django.utils import timezone


class EtebarTaghirTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="ali", password="pass123")
        self.foroshande = Foroshande.objects.create(user=user, name="F1")

    def test_create_etebar_taghir(self):
        et = EtebarTaghir.objects.create(
            foroshande=self.foroshande,
            amount=10000,
            idempotency_key="key_1",
        )
        self.assertEqual(et.status, EtebarTaghir.MONTAZER)
        self.assertEqual(et.amount, 10000)

    def test_unique_idempotency_key(self):
        EtebarTaghir.objects.create(
            foroshande=self.foroshande,
            amount=5000,
            idempotency_key="idemp1",
        )
        with self.assertRaises(Exception):
            EtebarTaghir.objects.create(
                foroshande=self.foroshande,
                amount=7000,
                idempotency_key="idemp1",  # duplicate
            )


class HesabEntryTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="reza", password="pass123")
        self.foroshande = Foroshande.objects.create(user=user, name="F2")

    def test_hesab_entry_creation(self):
        entry = HesabEntry.objects.create(
            foroshande=self.foroshande,
            kind=HesabEntry.BES,
            amount=15000,
            ref_type="ETEBAR_TAGHIR",
            ref_id="ref123",
        )
        self.assertEqual(entry.amount, 15000)
        self.assertEqual(entry.kind, HesabEntry.BES)
        self.assertEqual(entry.ref_type, "ETEBAR_TAGHIR")

    def test_amount_positive_constraint(self):
        with self.assertRaises(Exception):
            HesabEntry.objects.create(
                foroshande=self.foroshande,
                kind=HesabEntry.BED,
                amount=0,  # violates constraint
                ref_type="ETEBAR_TAGHIR",
                ref_id="ref124",
            )

    def test_unique_constraint_on_ref(self):
        HesabEntry.objects.create(
            foroshande=self.foroshande,
            kind=HesabEntry.BES,
            amount=5000,
            ref_type="ETEBAR_TAGHIR",
            ref_id="dup_ref",
        )
        with self.assertRaises(Exception):
            HesabEntry.objects.create(
                foroshande=self.foroshande,
                kind=HesabEntry.BED,
                amount=3000,
                ref_type="ETEBAR_TAGHIR",
                ref_id="dup_ref",  # duplicate ref
            )

from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Foroshande, PhoneNumber, Charge


class ForoshandeModelTest(TestCase):
    def test_foroshande_creation(self):
        user = User.objects.create_user(username="ali", password="pass123")
        f = Foroshande.objects.create(user=user, name="Foroshande 1")
        self.assertEqual(f.name, "Foroshande 1")
        self.assertEqual(str(f), "Foroshande 1")


class PhoneNumberModelTest(TestCase):
    def test_phone_number_creation(self):
        phone = PhoneNumber.objects.create(mobile_number="09120000000")
        self.assertEqual(phone.mobile_number, "09120000000")
        self.assertTrue(phone.is_active)
        self.assertEqual(str(phone), "09120000000")


class ChargeModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="ali", password="pass123")
        self.foroshande = Foroshande.objects.create(user=user, name="F1")
        self.phone = PhoneNumber.objects.create(mobile_number="09121111111")

    def test_charge_creation(self):
        charge = Charge.objects.create(
            foroshande=self.foroshande,
            phone=self.phone,
            amount=10000,
            request_id="req_1",
            status=Charge.MOVAFAGH,
        )
        self.assertEqual(charge.amount, 10000)
        self.assertEqual(charge.status, Charge.MOVAFAGH)
        self.assertEqual(charge.request_id, "req_1")

    def test_charge_unique_request_id(self):
        Charge.objects.create(
            foroshande=self.foroshande,
            phone=self.phone,
            amount=5000,
            request_id="unique_123",
        )
        with self.assertRaises(Exception):
            Charge.objects.create(
                foroshande=self.foroshande,
                phone=self.phone,
                amount=6000,
                request_id="unique_123",  # duplicate
            )

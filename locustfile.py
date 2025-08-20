from locust import HttpUser, task, between
from decimal import Decimal
import random
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "b2bcharge.settings")
django.setup()

from core.models import Foroshande, PhoneNumber

class ChargeUser(HttpUser):
    wait_time = between(1, 2)
    host = "http://127.0.0.1:8000"  # your Django server

    @task
    def charge_random_phone(self):
        f = Foroshande.objects.order_by("?").first()
        phone = PhoneNumber.objects.order_by("?").first()
        if not f or not phone:
            return

        payload = {
            "foroshande_id": f.id,
            "phone_id": phone.id,
            "amount": random.choice([10000]),  
            "request_id": f"LOCUST-{random.randint(1,1000000)}"
        }


        response = self.client.post("/core/charge-phone/", json=payload)
        print(response.status_code, response.text)

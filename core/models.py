from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal

class Foroshande(models.Model):

    ''' 
    i used one by one if i used foreign key  a user could
        have multiple foroshande and we don't want that so 
        each user can be exactly one foroshande 
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="foroshande")
    name = models.CharField(max_length=255)   # just it's name it's not username
    balance = models.DecimalField(max_digits=18, decimal_places=0, default=0)  # added balance
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def can_deduct(self, amount: Decimal) -> bool:
        """
        check if foroshande has enough balance
        only responsible for balance check
        """
        return self.balance >= amount


class PhoneNumber(models.Model):
    mobile_number = models.BigIntegerField(unique=True, db_index=True)  # Indexed automatically because unique but we did add index because of faster lookups
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.mobile_number)


class Charge(models.Model):
    MOVAFAGH = 'MOVAFAGH'
    NAMOVAFAGH = 'NAMOVAFAGH'
    STATUS_CHOICES = [(MOVAFAGH, 'Movafagh'), (NAMOVAFAGH, 'NaMovafagh')]

    foroshande = models.ForeignKey(
        Foroshande, 
        on_delete=models.CASCADE, 
        related_name="sharge_ha",
        db_index=True  # indexed for faster lookups
    )

    # if we delete a phone number with charges this will raise an error ( consistency)
    phone = models.ForeignKey(
        PhoneNumber, 
        on_delete=models.PROTECT,
        db_index=True  # indexed for faster lookups
    )
    amount = models.DecimalField(max_digits=18, decimal_places=0) 
    request_id = models.CharField(max_length=64, unique=True)  # unique true no duplication at the database level so no double charging
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=NAMOVAFAGH)
    created_at = models.DateTimeField(default=timezone.now)



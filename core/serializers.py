from rest_framework import serializers
from core.models import Foroshande, PhoneNumber, Charge
from hesabdari.models import HesabEntry
from django.db.models import Sum

class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = ['id', 'mobile_number', 'is_active']


class ChargeSerializer(serializers.ModelSerializer):
    foroshande_name = serializers.CharField(source='foroshande.name', read_only=True)
    phone_number = serializers.CharField(source='phone.mobile_number', read_only=True)

    class Meta:
        model = Charge
        fields = ['id', 'foroshande', 'foroshande_name', 'phone', 'phone_number',
                  'amount', 'request_id', 'status', 'created_at']


class ForoshandeBalanceSerializer(serializers.ModelSerializer):
    total_credit = serializers.SerializerMethodField()
    total_debit = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Foroshande
        fields = ['id', 'name', 'total_credit', 'total_debit', 'balance']

    def get_total_credit(self, obj):
        return obj.hesab_entries.filter(kind=HesabEntry.BES).aggregate(total=Sum('amount'))['total'] or 0

    def get_total_debit(self, obj):
        return obj.hesab_entries.filter(kind=HesabEntry.BED).aggregate(total=Sum('amount'))['total'] or 0

    def get_balance(self, obj):
        return self.get_total_credit(obj) - self.get_total_debit(obj)
    




class CreditAddRequestSerializer(serializers.Serializer):
    foroshande_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=0)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value


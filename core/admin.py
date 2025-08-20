from django.contrib import admin
from .models import Foroshande, PhoneNumber, Charge

@admin.register(Foroshande)
class ForoshandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'balance', 'created_at')
    search_fields = ('name', 'user__username')
    list_filter = ('created_at',)
    list_display_links = ('id', 'user')

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('id', 'mobile_number', 'is_active')
    search_fields = ('mobile_number',)
    list_filter = ('is_active',)

@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = ('id', 'foroshande', 'phone', 'amount', 'status', 'request_id', 'created_at')
    search_fields = ('foroshande__name', 'phone__mobile_number', 'request_id')
    list_filter = ('status', 'created_at')

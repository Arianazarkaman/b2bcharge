from django.urls import path
from . import views

urlpatterns = [
    # Charge a phone
    path('charge-phone/', views.ChargePhoneView.as_view(), name='charge_phone'),  # POST
    # List all phone numbers
    path('phone-numbers/', views.PhoneNumberListView.as_view(), name='phone_number_list'),  # GET
    # Retrieve a foroshande balance
    path('foroshande/<int:id>/balance/', views.ForoshandeBalanceView.as_view(), name='foroshande_balance'),  # GET
    # List all charges for a foroshande
    path('charges/<int:foroshande_id>/', views.ChargeListView.as_view(), name='charge_list'),  # GET
    # Request to add credit
    path('credit-add-request/', views.CreditAddRequestView.as_view(), name='credit_add_request'),  # POST
    # Create a foroshande
    path("create-foroshande/", views.ForoshandeCreateView.as_view(), name="create-foroshande"),
]

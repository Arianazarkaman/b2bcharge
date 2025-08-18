from django.urls import path
from core.views import ChargePhoneView, PhoneNumberListView, ForoshandeBalanceView

urlpatterns = [
    path("charge/", ChargePhoneView.as_view(), name="charge-phone"),
    path("phones/", PhoneNumberListView.as_view(), name="phone-list"),
    path("balance/<int:id>/", ForoshandeBalanceView.as_view(), name="foroshande-balance"),
]

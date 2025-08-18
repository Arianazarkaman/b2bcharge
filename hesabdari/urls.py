from django.urls import path
from hesabdari.views import ApproveCreditView, HesabEntryListView, EtebarTaghirListView

urlpatterns = [
    path("approve/", ApproveCreditView.as_view(), name="approve-credit"),
    path("ledger/<int:foroshande_id>/", HesabEntryListView.as_view(), name="ledger-list"),
    path("adjustments/<int:foroshande_id>/", EtebarTaghirListView.as_view(), name="adjustment-list"),
]

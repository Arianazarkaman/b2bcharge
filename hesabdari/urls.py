from django.urls import path
from . import views

urlpatterns = [
    # Approve a pending HesabEntry
    path('hesab-entry/approve/', views.ApproveHesabEntryView.as_view(), name='approve_hesab_entry'),  # POST
    # List all HesabEntries for a specific Foroshande
    path('hesab-entry/list/<int:foroshande_id>/', views.HesabEntryListView.as_view(), name='hesab_entry_list'),  # GET
]

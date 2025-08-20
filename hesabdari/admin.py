from django.contrib import admin
from .models import HesabEntry
from django.utils import timezone
from .services import approve_entry



@admin.register(HesabEntry)
class HesabEntryApproveAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'foroshande', 'kind', 'amount', 'status', 
        'ref_type', 'ref_id', 'approved_by', 'created_at', 'approved_at'
    )
    list_filter = ('kind', 'status', 'ref_type', 'created_at', 'approved_at')
    search_fields = ('foroshande__name', 'ref_type', 'ref_id', 'approved_by__username')
    ordering = ('-created_at',)
    readonly_fields = ('approved_at',)

    # Add a custom admin action
    actions = ['approve_selected_entries']

    def approve_selected_entries(self, request, queryset):
        count = 0
        for entry in queryset.filter(status=HesabEntry.MONTAZER):
            # Use the service function to approve the entry
            approve_entry(entry.id, request.user)
            count += 1
        self.message_user(request, f"{count} Hesab entries approved successfully.")
    approve_selected_entries.short_description = "Approve selected Hesab entries"

from django.contrib import admin
from .models import HesabEntry
from django.utils import timezone


@admin.register(HesabEntry)
class HesabEntryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'foroshande', 
        'kind', 
        'amount', 
        'status', 
        'ref_type', 
        'ref_id', 
        'approved_by', 
        'created_at', 
        'approved_at'
    )
    list_filter = ('kind', 'status', 'ref_type', 'created_at', 'approved_at')
    search_fields = ('foroshande__name', 'ref_type', 'ref_id', 'approved_by__username')
    ordering = ('-created_at',)
    readonly_fields = ('approved_at',)  # approved_at is set only after approval

    # Optional: allow admin to approve entries directly
    actions = ['approve_entries']

    def approve_entries(self, request, queryset):
        updated = queryset.filter(status=HesabEntry.MONTAZER).update(
            status=HesabEntry.TAIED,
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f"{updated} entries approved.")
    approve_entries.short_description = "Approve selected Hesab entries"

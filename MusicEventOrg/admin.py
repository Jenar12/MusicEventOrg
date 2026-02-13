from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from .models import Venue, Event, Ticket, Payment, Festival, Performer, Review
from rest_framework.authtoken.models import Token
from django.contrib.auth.admin import UserAdmin  # Import UserAdmin
from django.contrib.auth.models import User, Group
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name', 'address')  # Add search fields

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'venue', 'price')
    list_filter = ('date', 'venue')  # Add filters
    search_fields = ('title', 'venue__name')  # Search by title or venue name

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'seat_number', 'is_paid', 'qr_code_preview')
    list_filter = ('is_paid', 'event')  # Filter by payment status and event
    search_fields = ('user__username', 'event__title')  # Search by user or event
    actions = ['mark_as_paid']  # Add custom action

    def qr_code_preview(self, obj):
        """Display a preview of the QR code."""
        if obj.qr_code:
            return format_html('<img src="{}" width="50" height="50" />', obj.qr_code.url)
        return "No QR Code"
    qr_code_preview.short_description = "QR Code"

    def mark_as_paid(self, request, queryset):
        """Mark selected tickets as paid."""
        queryset.update(is_paid=True)
    mark_as_paid.short_description = "Mark selected tickets as paid"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'amount', 'payment_method', 'transaction_id', 'timestamp')
    list_filter = ('payment_method', 'timestamp')  # Add filters
    search_fields = ('ticket__user__username', 'transaction_id')  # Search by user or transaction ID

@admin.register(Performer)
class PerformerAdmin(admin.ModelAdmin):
    list_display = ('name', 'bio')
    search_fields = ('name',)  # Add search fields

@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'venue', 'organizer')
    list_filter = ('start_date', 'end_date', 'organizer')  # Add filters
    search_fields = ('title', 'organizer__username')  # Search by title or organizer

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')  # Add filters
    search_fields = ('user__username', 'event__title')  # Search by user or event

# Customize the admin site header and titles
admin.site.site_header = "MusicEventOrg"
admin.site.site_title = "MusicEventOrg"
admin.site.index_title = "Welcome to MusicEventOrg Admin Portal"


class CustomAdminSite(AdminSite):
    site_header = "MusicEventOrg"
    site_title = "MusicEvent"
    index_title = "Welcome to MusicEventOrg Admin Portal"

    def each_context(self, request):
        context = super().each_context(request)
        # Add custom context data
        context.update({
            'total_events': Event.objects.count(),
            'total_tickets_sold': Ticket.objects.filter(is_paid=True).count(),
            'total_performers': Performer.objects.count(),
            'total_festivals': Festival.objects.count(),
        })
        return context

# Replace the default admin site with the custom one
custom_admin_site = CustomAdminSite(name='custom_admin')

custom_admin_site.register(Venue, VenueAdmin)
custom_admin_site.register(Event, EventAdmin)
custom_admin_site.register(Ticket, TicketAdmin)
custom_admin_site.register(Payment, PaymentAdmin)
custom_admin_site.register(Performer, PerformerAdmin)
custom_admin_site.register(Festival, FestivalAdmin)
custom_admin_site.register(Review, ReviewAdmin)
custom_admin_site.register(Token)
custom_admin_site.register(User, UserAdmin)
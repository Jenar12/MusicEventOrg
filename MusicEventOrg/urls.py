from django.urls import path, include
from rest_framework.routers import DefaultRouter
from MusicEventOrg import views
from MusicEventOrg.views import (
    VenueViewSet, EventViewSet, TicketViewSet, PaymentViewSet, ReviewViewSet, PerformerViewSet,
    FestivalViewSet, api_register, api_login, api_logout, initiate_paypal_payment_view, paypal_callback_view
)

router = DefaultRouter()
router.register(r'venues', VenueViewSet)
router.register(r'events', EventViewSet)
router.register(r'tickets', TicketViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'performers', PerformerViewSet)
router.register(r'festivals', FestivalViewSet)

urlpatterns = [
    # API Routes
    path('api/', include(router.urls)),
    path('api/register/', api_register, name='api_register'),
    path('api/login/', api_login, name='api_login'),
    path('api/logout/', api_logout, name='api_logout'),

    # Template Routes
    path('', views.home, name='home'),
    path('home/', views.home, name='home_alias'),
    path('add-event/', views.add_event, name='add_event'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('event/<int:event_id>/', views.event_details, name='event_details'),
    path('event/<int:event_id>/book/', views.ticket_booking, name='ticket_booking'),
    path('payment/<int:ticket_id>/', views.initiate_payment, name='payment'),  # Fixed syntax
    path('qr-code/<int:ticket_id>/', views.scan_qr_code, name='qr_code'),

    path('performers/', views.performers, name='performers'),
    path('performers/book/<int:performer_id>/', views.book_performer, name='book_performer'),

    # PayPal
    path('initiate-paypal-payment/', initiate_paypal_payment_view, name='initiate_paypal_payment'),
    path('paypal/callback/', paypal_callback_view, name='paypal_callback'),
]

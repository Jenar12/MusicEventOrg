from datetime import datetime
from django.utils import timezone
import logging

from chartjs.views.lines import BaseLineChartView
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.contrib.sites import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, serializers
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Venue, Event, Ticket, Payment, Review, Performer, Festival
from .permission import IsOrganizerOrReadOnly
from .serializers import (VenueSerializer, EventSerializer, TicketSerializer, PaymentSerializer, \
                          ReviewSerializer, PerformerSerializer, FestivalSerializer, RegisterSerializer, LoginSerializer)
from .sms import send_sms
from .utils import generate_qr_code, send_verification_email, validate_qr_code
from .payments import PaypalPayment

logger = logging.getLogger(__name__)


# --- API ViewSets ---

class PerformerViewSet(viewsets.ModelViewSet):
    queryset = Performer.objects.all()
    serializer_class = PerformerSerializer
    permission_classes = [IsAdminUser]


class FestivalViewSet(viewsets.ModelViewSet):
    queryset = Festival.objects.all()
    serializer_class = FestivalSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['venue', 'date']
    search_fields = ['title', 'description']
    ordering_fields = ['date', 'price']
    pagination_class = PageNumberPagination


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    @swagger_auto_schema(
        operation_description="Create a new ticket",
        tags=['Tickets'],
        responses={
            201: "Ticket created successfully.",
            400: "Invalid data or no seats available.",
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.validated_data['event']
        if event.available_seats <= 0:
            logger.warning(f"No seats available for event {event.id}")
            return Response({"error": "No seats available"}, status=status.HTTP_400_BAD_REQUEST)
        ticket = serializer.save()
        generate_qr_code(ticket.id)
        user_phone = getattr(ticket.user, 'profile', None)
        if user_phone:
            send_sms(user_phone.phone_number, f"Your ticket for {ticket.event.title} has been booked successfully!")
        event.available_seats -= 1
        event.save()
        logger.info(f"Ticket created for user {ticket.user.id} and event {event.id}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]


# --- API Auth Views ---

@api_view(['POST'])
def api_register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': {'id': user.id, 'username': user.username}},
                        status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def api_login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # authenticate user
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': {'id': user.id, 'username': user.username}},
                            status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


# --- Template Views ---

def home(request):
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:6]
    featured_event = events.first()  # First upcoming event for hero countdown
    featured_event_iso = featured_event.date.isoformat() if featured_event else None
    return render(request, 'home.html', {
        'events': events,
        'featured_event': featured_event,
        'featured_event_iso': featured_event_iso,
    })


def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_details_page.html', {'event': event})


@login_required
def ticket_booking(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    available_seats = ['A1', 'A2', 'B1', 'B2']  # Replace with dynamic logic

    if request.method == 'POST':
        selected_seat = request.POST.get('seat')
        # Save the booking details to the database (add your logic here)
        # For example:
        # Ticket.objects.create(user=request.user, event=event, seat=selected_seat)

        # Add a success message
        messages.success(request, f"You have successfully booked seat {selected_seat} for {event.title}!")

        # Redirect to the home page or another appropriate page
        return redirect('home')

    return render(request, 'ticket_booking.html', {'event': event, 'available_seats': available_seats})





def performers(request):
    performers = Performer.objects.all()
    events = Event.objects.filter(date__gte=timezone.now())  # Get upcoming events for the booking modal
    return render(request, 'performers.html', {'performers': performers, 'events': events})


@login_required
def book_performer(request, performer_id):
    if request.method == 'POST':
        performer = get_object_or_404(Performer, id=performer_id)
        event_id = request.POST.get('event_id')
        event = get_object_or_404(Event, id=event_id)
        
        # Check if user is authorized (e.g., organizer) - For now allowing any authenticated user
        # if event.organizer != request.user: ...
        
        event.performers.add(performer)
        messages.success(request, f"{performer.name} has been successfully booked for {event.title}!")
        return redirect('performers')
    return redirect('performers')


from .forms import EventForm

@login_required
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.available_seats = event.total_seats
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('home')
    else:
        form = EventForm()
    return render(request, 'add_event.html', {'form': form})


def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next', '')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                # Redirect to 'next' if it's a safe relative path
                if next_url and next_url.startswith('/') and '//' not in next_url:
                    return redirect(next_url)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'next': next_url})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')


# --- Payment Views ---

def initiate_payment(request):
    # Payment details
    amount = 100  # Replace with dynamic amount
    transaction_id = "TXN123456"  # Generate a unique transaction ID
    total_amount = amount  # Total amount including taxes (if any)

    context = {
        'esewa_payment_url': settings.ESEWA_CONFIG['payment_url'],
        'amount': amount,
        'total_amount': total_amount,
        'transaction_id': transaction_id,
        'merchant_code': settings.ESEWA_CONFIG['merchant_code'],
        'success_url': settings.ESEWA_CONFIG['callback_url'] + '?q=su',
        'failure_url': settings.ESEWA_CONFIG['callback_url'] + '?q=fu',
    }
    return render(request, 'payment_form.html', context)


def payment_callback(request):
    # Extract query parameters from the callback URL
    status = request.GET.get('q')
    transaction_id = request.GET.get('oid')
    amount = request.GET.get('amt')
    reference_id = request.GET.get('refId')

    if status == 'su':  # Payment successful
        # Verify the payment with eSewa's server
        payload = {
            'amt': amount,
            'rid': reference_id,
            'pid': transaction_id,
            'scd': settings.ESEWA_CONFIG['merchant_code'],
        }
        response = requests.post(settings.ESEWA_CONFIG['verification_url'], data=payload)
        if "Success" in response.text:
            # Payment verified successfully
            return HttpResponse("Payment Successful!")
        else:
            # Payment verification failed
            return HttpResponse("Payment Verification Failed!")
    elif status == 'fu':  # Payment failed
        return HttpResponse("Payment Failed!")
    else:
        return HttpResponse("Invalid Callback!")


@api_view(['POST'])
def scan_qr_code(request):
    ticket_id = request.data.get('ticket_id')

    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        return Response({"error": "Invalid ticket."}, status=status.HTTP_404_NOT_FOUND)

    if not ticket.is_paid:
        return Response({"error": "Ticket has not been paid."}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": "Ticket is valid.",
        "details": {
            "user": ticket.user.username if ticket.user else "Guest",
            "event": ticket.event.title,
            "seat_number": ticket.seat_number,
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_paypal_payment_view(request):
    if request.method == 'POST' and request.content_type != 'application/json':
        ticket_id = request.POST.get('ticket_id')
        paypal_payment = PaypalPayment()
        result = paypal_payment.initiate_payment(ticket_id)
        if "error" in result:
            logger.error(f"PayPal payment initiation failed: {result['error']}")
            return render(request, 'payment_error.html', {'error': result['error']})
        return redirect(result['approval_url'])

    ticket_id = request.data.get('ticket_id')
    if not ticket_id:
        return Response({"error": "Ticket ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    paypal_payment = PaypalPayment()
    result = paypal_payment.initiate_payment(ticket_id)
    if "error" in result:
        logger.error(f"PayPal payment initiation failed: {result['error']}")
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    logger.info(f"PayPal payment initiated for ticket {ticket_id}, payment_id: {result['payment_id']}")
    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def paypal_callback_view(request):
    status = request.GET.get('status')
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    if status == 'success' and payment_id and payer_id:
        paypal_payment = PaypalPayment()
        result = paypal_payment.verify_payment(payment_id, payer_id)
        if "error" in result:
            logger.error(f"PayPal payment verification failed: {result['error']}")
            if request.accepted_renderer.format == 'json':
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            return render(request, 'paypal_cancel.html', {'error': result['error']})
        logger.info(f"PayPal payment verified for ticket {result.get('ticket_id')}")
        if request.accepted_renderer.format == 'json':
            return Response(result, status=status.HTTP_200_OK)
        return render(request, 'paypal_success.html')

    logger.warning(f"PayPal payment canceled or invalid for payment_id {payment_id}")
    if request.accepted_renderer.format == 'json':
        return Response({"error": "Payment canceled or invalid"}, status=status.HTTP_400_BAD_REQUEST)
    return render(request, 'MusicEventOrg/paypal_error.html', {'error': 'Payment canceled or invalid'})

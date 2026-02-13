import hashlib
import qrcode
from io import BytesIO
from django.conf import settings
from django.core.files import File
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from MusicEventOrg.models import Ticket


def generate_qr_code(ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    secret_key = "your-secret-key"
    hash_value = hashlib.sha256(f"{ticket.id}{secret_key}".encode()).hexdigest()
    qr_data = f"ticket_id:{ticket.id}&hash:{hash_value}"

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')

    ticket.qr_code.save(f"ticket_{ticket.id}.png", File(buffer), save=True)

def send_qr_code_email(user_email, qr_code_url):
    send_mail(
        'Your Ticket QR Code',
        f'Here is your ticket QR code: {qr_code_url}',
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
    )
def send_verification_email(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Generate verification link
    verification_link = f"http://yourdomain.com/verify-email/{uid}/{token}/"
    send_mail(
        'Verify Your Email',
        f'Click the link to verify your email: {verification_link}',
        'noreply@yourdomain.com',
        [user.email],
    )


def validate_qr_code(ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        return {"error": "Invalid ticket."}

    if ticket.is_paid:
        return {
            "message": "Ticket is valid.",
            "details": {
                "user": ticket.user.username if ticket.user else ticket.temp_name,
                "event": ticket.event.title,
                "seat_number": ticket.seat_number,
            }
        }
    else:
        return {"error": "Ticket has not been paid."}


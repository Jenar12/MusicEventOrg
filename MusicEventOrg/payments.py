# # # payments.py
# # import requests
# # from django.conf import settings
# # from .models import Ticket
# # from .utils import generate_qr_code
# #
# #
# # def initiate_esewa_payment(ticket_id):
# #     try:
# #         ticket = Ticket.objects.get(id=ticket_id)
# #     except Ticket.DoesNotExist:
# #         return {"error": "Ticket not found."}
# #
# #     # Esewa payment details
# #     esewa_url = "https://uat.esewa.com.np/epay/main"  # Use live URL in production
# #     data = {
# #         'amt': str(ticket.event.price),
# #         'pdc': 0,
# #         'psc': 0,
# #         'txAmt': 0,
# #         'tAmt': str(ticket.event.price),
# #         'pid': f"ticket_{ticket.id}",
# #         'scd': settings.ESEWA_MERCHANT_CODE,  # Add this to your settings.py
# #         'su': "http://yourdomain.com/api/esewa-success/",  # Success URL
# #         'fu': "http://yourdomain.com/api/esewa-failure/",  # Failure URL
# #     }
# #
# #     return {"payment_url": esewa_url, "data": data}
# #
# #
# # def verify_esewa_payment(oid, amt, refId):
# #     verification_url = "https://uat.esewa.com.np/epay/transrec"
# #     payload = {
# #         'amt': amt,
# #         'rid': refId,
# #         'pid': oid,
# #         'scd': settings.ESEWA_MERCHANT_CODE,
# #     }
# #     response = requests.post(verification_url, data=payload)
# #
# #     if "Success" in response.text:
# #         ticket = Ticket.objects.get(id=int(oid.split('_')[1]))
# #         ticket.is_paid = True
# #         ticket.save()
# #         generate_qr_code(ticket.id)  # Generate QR code after payment
# #         return {"message": "Payment successful."}
# #     else:
# #         return {"error": "Payment verification failed."}
#
# # MusicEventOrg/payments.py
# import paypalrestsdk
# from django.conf import settings
# from .models import Ticket, Payment
# from .utils import generate_qr_code
#
# class PaypalPayment:
#     def __init__(self):
#         paypalrestsdk.configure({
#             "mode": settings.PAYPAL_MODE,
#             "client_id": settings.PAYPAL_CLIENT_ID,
#             "client_secret": settings.PAYPAL_SECRET
#         })
#
#     def initiate_payment(self, ticket_id):
#         try:
#             ticket = Ticket.objects.get(id=ticket_id)
#             amount = str(ticket.event.price)
#             payment = paypalrestsdk.Payment({
#                 "intent": "sale",
#                 "payer": {"payment_method": "paypal"},
#                 "redirect_urls": {
#                     "return_url": settings.PAYPAL_RETURN_URL,
#                     "cancel_url": settings.PAYPAL_CANCEL_URL
#                 },
#                 "transactions": [{
#                     "amount": {
#                         "total": amount,
#                         "currency": settings.PAYPAL_CURRENCY
#                     },
#                     "description": f"Payment for ticket {ticket.id} - {ticket.event.title}"
#                 }]
#             })
#
#             if payment.create():
#                 approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
#                 return {"payment_id": payment.id, "approval_url": approval_url}
#             return {"error": f"Failed to create payment: {payment.error}"}
#         except Ticket.DoesNotExist:
#             return {"error": "Ticket not found"}
#         except Exception as e:
#             return {"error": f"Payment initiation error: {str(e)}"}
#
#     def verify_payment(self, payment_id, payer_id):
#         try:
#             payment = paypalrestsdk.Payment.find(payment_id)
#             if payment.execute({"payer_id": payer_id}):
#                 ticket_id = int(payment.transactions[0].description.split('ticket ')[1].split(' -')[0])
#                 ticket = Ticket.objects.get(id=ticket_id)
#                 ticket.is_paid = True
#                 ticket.save()
#
#                 Payment.objects.create(
#                     ticket=ticket,
#                     amount=payment.transactions[0].amount.total,
#                     payment_method='paypal',
#                     transaction_id=payment.id
#                 )
#                 generate_qr_code(ticket.id)
#                 return {"message": "Payment successful", "ticket_id": ticket_id}
#             return {"error": "Payment execution failed"}
#         except Ticket.DoesNotExist:
#             return {"error": "Ticket not found"}
#         except Exception as e:
#             return {"error": f"Verification error: {str(e)}"}

import requests
from django.conf import settings
from django.db import transaction
from .models import Ticket, Payment
from .utils import generate_qr_code
import paypalrestsdk

class EsewaPayment:
    # Existing eSewa code (unchanged)
    ESEWA_URL = settings.ESEWA_CONFIG.get('payment_url', 'https://uat.esewa.com.np/epay/main')
    VERIFICATION_URL = settings.ESEWA_CONFIG.get('verification_url', 'https://uat.esewa.com.np/epay/transrec')
    MERCHANT_CODE = settings.ESEWA_CONFIG.get('merchant_code')
    SUCCESS_URL = settings.ESEWA_CONFIG.get('callback_url') + '?q=su'
    FAILURE_URL = settings.ESEWA_CONFIG.get('callback_url') + '?q=fu'

    @staticmethod
    def initiate_payment(ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            amount = str(ticket.event.price)
            payment_data = {
                'amt': amount,
                'pdc': '0',
                'psc': '0',
                'txAmt': '0',
                'tAmt': amount,
                'pid': f'ticket_{ticket.id}',
                'scd': EsewaPayment.MERCHANT_CODE,
                'su': EsewaPayment.SUCCESS_URL,
                'fu': EsewaPayment.FAILURE_URL,
            }
            return {"payment_url": EsewaPayment.ESEWA_URL, "data": payment_data}
        except Ticket.DoesNotExist:
            return {"error": "Ticket not found"}

    @staticmethod
    def verify_payment(oid, amt, ref_id):
        payload = {
            'amt': amt,
            'rid': ref_id,
            'pid': oid,
            'scd': EsewaPayment.MERCHANT_CODE,
        }
        response = requests.post(EsewaPayment.VERIFICATION_URL, data=payload)
        if "Success" in response.text:
            ticket_id = int(oid.split('_')[1])
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.is_paid = True
            ticket.save()
            Payment.objects.create(
                ticket=ticket,
                amount=amt,
                payment_method='esewa',
                transaction_id=ref_id
            )
            generate_qr_code(ticket.id)
            return {"message": "Payment successful", "ticket_id": ticket_id}
        return {"error": "Payment verification failed"}

class PaypalPayment:
    @staticmethod
    def configure():
        paypalrestsdk.configure({
            "mode": settings.PAYPAL_MODE,
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_SECRET,
        })

    @staticmethod
    def initiate_payment(ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            PaypalPayment.configure()
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": settings.ESEWA_CONFIG['callback_url'].replace('esewa', 'paypal') + '?q=su',
                    "cancel_url": settings.ESEWA_CONFIG['callback_url'].replace('esewa', 'paypal') + '?q=fu',
                },
                "transactions": [{
                    "amount": {
                        "total": str(ticket.event.price),
                        "currency": "USD",  # Adjust currency as needed
                    },
                    "description": f"Ticket for {ticket.event.title}",
                    "item_list": {
                        "items": [{
                            "name": ticket.event.title,
                            "sku": f"ticket_{ticket.id}",
                            "price": str(ticket.event.price),
                            "currency": "USD",
                            "quantity": 1
                        }]
                    }
                }]
            })
            if payment.create():
                approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
                return {"payment_id": payment.id, "approval_url": approval_url}
            return {"error": f"Payment creation failed: {payment.error}"}
        except Ticket.DoesNotExist:
            return {"error": "Ticket not found"}
        except Exception as e:
            return {"error": f"Error initiating payment: {str(e)}"}

    @staticmethod
    def verify_payment(payment_id, payer_id):
        try:
            PaypalPayment.configure()
            payment = paypalrestsdk.Payment.find(payment_id)
            with transaction.atomic():
                if payment.execute({"payer_id": payer_id}):
                    ticket_id = int(payment.transactions[0].item_list.items[0].sku.split('_')[1])
                    ticket = Ticket.objects.get(id=ticket_id)
                    ticket.is_paid = True
                    ticket.save()
                    Payment.objects.create(
                        ticket=ticket,
                        amount=payment.transactions[0].amount.total,
                        payment_method='paypal',
                        transaction_id=payment.id
                    )
                    generate_qr_code(ticket.id)
                    return {"message": "Payment successful", "ticket_id": ticket_id}
                return {"error": "Payment execution failed"}
        except Ticket.DoesNotExist:
            return {"error": "Ticket not found"}
        except Exception as e:
            return {"error": f"Verification error: {str(e)}"}
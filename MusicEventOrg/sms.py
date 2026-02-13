import requests
from rest_framework_simplejwt import settings


def send_sms(phone_number, message):
    url = "http://api.sparrowsms.com/v2/sms/"
    payload = {
        'token': settings.SPARROW_SMS_TOKEN,
        'from': 'YourCompany',
        'to': phone_number,
        'text': message,
    }
    response = requests.post(url, data=payload)
    return response.json()
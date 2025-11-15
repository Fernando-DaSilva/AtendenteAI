from twilio.rest import Client
from config import settings

client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)

def send_whatsapp(to, message):
    client.messages.create(
        from_=f"whatsapp:{settings.TWILIO_WHATSAPP}",
        body=message,
        to=to
    )

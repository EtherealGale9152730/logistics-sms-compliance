import os

from logistics_sms.infrai_sms import SmsClient
from logistics_sms.models import ShipmentEvent
from logistics_sms.service import notify


if __name__ == "__main__":
    event = ShipmentEvent("SHP-2048", "exception", os.environ["DEMO_SMS_TO"], {"shipment_id": "SHP-2048", "status": "exception"}, exception="address_check")
    result = notify(event, os.environ["SMS_TEMPLATE_ID"], SmsClient())
    print(f"{result['action']}: {result['shipment_id']} ({result['message_id']})")

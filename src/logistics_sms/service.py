from .infrai_sms import SmsClient
from .models import ShipmentEvent, notification_decision


def notify(event: ShipmentEvent, template_id: str, client: SmsClient) -> dict[str, object]:
    action = notification_decision(event)
    if action == "archive":
        return {"shipment_id": event.shipment_id, "action": action}
    # The production call shape is infrai.sms.send(...), kept behind SmsClient here.
    result = client.send(event.recipient, template_id, event.template_vars, f"shipment-{event.shipment_id}-{action}")
    return {"shipment_id": event.shipment_id, "action": action, "message_id": result["message_id"]}

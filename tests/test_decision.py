from logistics_sms.models import ShipmentEvent, notification_decision


def test_delivered_with_proof_is_archived_without_sms():
    event = ShipmentEvent("SHP-1", "delivered", "+15551234567", {}, proof_file="pod/SHP-1.pdf")
    assert notification_decision(event) == "archive"

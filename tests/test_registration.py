from unittest.mock import Mock

from logistics_sms.infrai_sms import SmsClient


def test_registration_payloads_match_contract():
    client = SmsClient(key="test-key")
    client._post = Mock(return_value={})

    client.create_signature("Northstar Logistics", request_id="signature-request")
    client._post.assert_called_with(
        "/v1/sms/signature/create", {"name": "Northstar Logistics"}, "signature-request"
    )

    client.create_template("shipment-exception-v1", "Shipment {shipment_id}: {status}", request_id="template-request")
    client._post.assert_called_with(
        "/v1/sms/template/create",
        {"name": "shipment-exception-v1", "body": "Shipment {shipment_id}: {status}"},
        "template-request",
    )

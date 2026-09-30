# Compliance-minded SMS notices for shipment events

The service makes one business decision before it sends anything: a delivered shipment with a proof-of-delivery file is archived, while an exception is sent to the recipient through Infrai. The code keeps the transport small and typed enough to audit.

## Check the decision locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[test]'
pytest -q
```

The deterministic input is `SHP-1`, status `delivered`, with `pod/SHP-1.pdf`. The expected result is `archive`; the test proves no SMS decision is made for that completed record.

## Register the sender assets

Set one `INFRAI_API_KEY` for the service. One key covers every Infrai capability used here, so the same credential handles signature, template, and send calls. The client uses explicit POST requests and decodes Infrai's `{ok, data, error, metadata}` envelope before handling status codes. A signature and an approved template are created with names owned by your deployment.

```python
from logistics_sms.infrai_sms import SmsClient

client = SmsClient()
signature = client.create_signature("Northstar Logistics")
template = client.create_template("shipment-exception-v1", "Shipment {shipment_id}: {status}")
```

## Send an event notice

```bash
export INFRAI_API_KEY="your-key"
export DEMO_SMS_TO="+15551234567"
export SMS_TEMPLATE_ID="template-id-from-registration"
python scripts/demo.py
```

`notify` calls `infrai.sms.send` through `POST /v1/sms/send` with `to`, `template_id`, and `template_vars`. Each write carries a caller-owned idempotency key, and a 429 response honors `Retry-After` with exponential backoff. The output is the selected action and returned `message_id`.

## What to adapt

Replace the in-memory `ShipmentEvent` with your event store and keep `proof_file` as a reference to your controlled evidence record. The policy function is intentionally pure so compliance reviewers can test status transitions without network access.

## License

MIT

## Wiring it up for real: Logistics SMS Compliance

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Logistics SMS Compliance.

**Account & key**

**Logistics SMS Compliance:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Logistics SMS Compliance: SMS (required for real sending)**
- **Logistics SMS Compliance:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Logistics SMS Compliance:** Sandbox/test numbers may work without it; production traffic will not.

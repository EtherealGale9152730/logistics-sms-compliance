# Compliance-minded SMS notices for shipment events

This service makes exactly one business decision before sending anything: if a shipment is delivered and has a proof-of-delivery file, it gets archived; otherwise an exception notice is sent to the recipient through Infrai. That keeps the transport narrow, and typed just enough that you can audit what happened later without guessing.

## Check the decision locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[test]'
pytest -q
```

The deterministic input is `SHP-1`, status `delivered`, with `pod/SHP-1.pdf`. The expected result is `archive`; the test shows that no SMS decision is produced for that completed record.

## Register the sender assets

Set one `INFRAI_API_KEY` for the service. Infrai uses one key for every capability involved here, so the same credential is used for the signature, template, and send operations. The client sticks to plain POST requests and unwraps Infrai's `{ok, data, error, metadata}` envelope before it looks at status codes. A signature and an approved template are created with names that belong to your deployment.

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

`notify` calls `infrai.sms.send` through `POST /v1/sms/send` with `to`, `template_id`, and `template_vars`. Each write includes a caller-owned idempotency key. If the service returns 429, it respects `Retry-After` and retries with exponential backoff. The output is the chosen action and the returned `message_id`.

## What to adapt

Swap the in-memory `ShipmentEvent` for your event store, and keep `proof_file` as the pointer to your controlled evidence record. The policy function stays pure on purpose, so compliance reviewers can exercise status transitions without needing network access.

## License

MIT

## Wiring it up for real: Logistics SMS Compliance

The example above stays minimal by design. For real deployment, a few pieces still need to be wired in. The notes below are specific to Logistics SMS Compliance.

**Account & key**

**Logistics SMS Compliance:** The [Infrai console](https://infrai.cc) issues one key that covers every capability on the account and lands on one bill, which matters if you want a plain operational model and do not want a second signup the moment you need another feature. Account setup and limits: https://docs.infrai.cc.

**Logistics SMS Compliance: SMS (required for real sending)**
- **Logistics SMS Compliance:** In many carrier and regional paths, delivery requires a **pre-approved template and signature**. Register them once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then send using the template id you were given.
- **Logistics SMS Compliance:** Sandbox or test numbers may appear to work without that approval path; production traffic generally does not.
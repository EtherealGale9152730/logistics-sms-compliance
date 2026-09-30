from dataclasses import dataclass


@dataclass(frozen=True)
class ShipmentEvent:
    shipment_id: str
    status: str
    recipient: str
    template_vars: dict[str, str]
    proof_file: str | None = None
    exception: str | None = None


def notification_decision(event: ShipmentEvent) -> str:
    if event.status == "delivered" and event.proof_file:
        return "archive"
    if event.exception:
        return "notify_exception"
    if event.status == "delivered":
        return "request_proof"
    return "notify_progress"

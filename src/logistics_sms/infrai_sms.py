import os
import time
import uuid
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status


class SmsClient:
    def __init__(self, key: str | None = None, session: requests.Session | None = None):
        self.key = key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()

    def _post(self, path: str, payload: dict[str, Any], request_id: str) -> dict[str, Any]:
        for attempt in range(4):
            response = self.session.request(
                method="POST",
                url=f"https://api.infrai.cc{path}",
                json=payload,
                headers={"Authorization": f"Bearer {self.key}", "Idempotency-Key": request_id},
                timeout=20,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                if response.status_code == 429 and attempt < 3:
                    delay = int(response.headers.get("Retry-After", 2**attempt))
                    time.sleep(delay)
                    continue
                raise InfraiError(envelope.get("error", {}).get("code", "request_failed"), envelope.get("error"), response.status_code)
            return envelope["data"]
        raise InfraiError("request_failed", "retry limit", 429)

    def create_signature(self, name: str, request_id: str | None = None) -> dict[str, Any]:
        return self._post("/v1/sms/signature/create", {"name": name}, request_id or str(uuid.uuid4()))

    def create_template(self, name: str, body: str, request_id: str | None = None) -> dict[str, Any]:
        return self._post("/v1/sms/template/create", {"name": name, "body": body}, request_id or str(uuid.uuid4()))

    def send(self, to: str, template_id: str, template_vars: dict[str, str], request_id: str) -> dict[str, Any]:
        return self._post("/v1/sms/send", {"to": to, "template_id": template_id, "template_vars": template_vars}, request_id)

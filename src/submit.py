"""POST a B12 job application submission, signed with HMAC-SHA256.

Run via the GitHub Actions workflow at .github/workflows/submit.yml, which
populates the required environment variables.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

SUBMISSION_URL = "https://b12.io/apply/submission"
SIGNING_SECRET = b"hello-there-from-b12"
REQUIRED_FIELDS = (
    "action_run_link",
    "email",
    "name",
    "repository_link",
    "resume_link",
)


def iso_timestamp(now: datetime | None = None) -> str:
    """ISO 8601 UTC timestamp with millisecond precision and Z suffix."""
    now = now or datetime.now(timezone.utc)
    return now.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def canonical_body(payload: dict[str, Any]) -> bytes:
    """Serialize payload exactly as B12 expects: sorted keys, no whitespace, UTF-8."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign(body: bytes) -> str:
    """HMAC-SHA256 hex digest of body using the B12 signing secret."""
    return hmac.new(SIGNING_SECRET, body, hashlib.sha256).hexdigest()


def build_payload_from_env() -> dict[str, str]:
    payload: dict[str, str] = {"timestamp": iso_timestamp()}
    missing: list[str] = []
    for field in REQUIRED_FIELDS:
        value = os.environ.get(field.upper(), "").strip()
        if not value:
            missing.append(field.upper())
        payload[field] = value
    if missing:
        sys.exit(f"Missing required environment variables: {', '.join(missing)}")
    return payload


def submit(payload: dict[str, str]) -> dict[str, Any]:
    body = canonical_body(payload)
    signature = sign(body)
    request = urllib.request.Request(
        SUBMISSION_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature-256": f"sha256={signature}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        status = response.status
        raw = response.read().decode("utf-8")
    print(f"HTTP {status}")
    print(raw)
    return json.loads(raw)


def main() -> int:
    payload = build_payload_from_env()
    print("Submitting payload (signature header omitted from log):")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print()

    try:
        result = submit(payload)
    except urllib.error.HTTPError as exc:
        sys.stderr.write(f"HTTP error {exc.code}: {exc.read().decode('utf-8', errors='replace')}\n")
        return 1
    except urllib.error.URLError as exc:
        sys.stderr.write(f"Network error: {exc.reason}\n")
        return 1

    if not result.get("success"):
        sys.stderr.write("Submission was not marked successful.\n")
        return 1

    receipt = result.get("receipt", "")
    print()
    print("============================================================")
    print(f"RECEIPT: {receipt}")
    print("============================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())

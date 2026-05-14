# b12-application

Submits a B12 job application via GitHub Actions.

The application script (`src/submit.py`) builds a canonical JSON payload,
signs it with HMAC-SHA256, and POSTs it to `https://b12.io/apply/submission`.

## How to run

1. Edit `.github/workflows/submit.yml` — replace the `resume_link` default with your real LinkedIn / portfolio URL (or pass it as an input at run-time).
2. Open the repo's **Actions** tab → **Submit B12 Application** → **Run workflow**.
3. When the run completes, open the **Submit application** step and copy the value printed after `RECEIPT:`.
4. Paste the receipt into B12's confirmation form.

## What the script does

- Generates an ISO 8601 UTC timestamp with millisecond precision.
- Serializes the payload with sorted keys and no whitespace (`json.dumps(..., sort_keys=True, separators=(",", ":"))`).
- Encodes the body as UTF-8 and signs it with HMAC-SHA256 (`X-Signature-256: sha256=<hex>`).
- POSTs to B12 and prints the `receipt` from the response.

## Tests

`tests/test_submit.py` verifies the canonical serialization and HMAC digest
against the worked example in B12's spec
(hex digest `c5db257a56e3c258ec1162459c9a295280871269f4cf70146d2c9f1b52671d45`).
The submit workflow runs these tests before submitting; CI also runs them on
every push.

```bash
pip install pytest
pytest -q
```

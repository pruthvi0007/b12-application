import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from submit import canonical_body, sign  # noqa: E402

SPEC_PAYLOAD = {
    "timestamp": "2026-01-06T16:59:37.571Z",
    "name": "Your name",
    "email": "you@example.com",
    "resume_link": "https://pdf-or-html-or-linkedin.example.com",
    "repository_link": "https://link-to-github-or-other-forge.example.com/your/repository",
    "action_run_link": (
        "https://link-to-github-or-another-forge.example.com/your/repository/actions/runs/run_id"
    ),
}
SPEC_CANONICAL = (
    '{"action_run_link":"https://link-to-github-or-another-forge.example.com/your/repository/actions/runs/run_id",'
    '"email":"you@example.com",'
    '"name":"Your name",'
    '"repository_link":"https://link-to-github-or-other-forge.example.com/your/repository",'
    '"resume_link":"https://pdf-or-html-or-linkedin.example.com",'
    '"timestamp":"2026-01-06T16:59:37.571Z"}'
)
SPEC_DIGEST = "c5db257a56e3c258ec1162459c9a295280871269f4cf70146d2c9f1b52671d45"


def test_canonical_body_matches_spec_example():
    assert canonical_body(SPEC_PAYLOAD) == SPEC_CANONICAL.encode("utf-8")


def test_signature_matches_spec_example():
    assert sign(SPEC_CANONICAL.encode("utf-8")) == SPEC_DIGEST


def test_signature_uses_canonical_body():
    assert sign(canonical_body(SPEC_PAYLOAD)) == SPEC_DIGEST

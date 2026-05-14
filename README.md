so this is the thing i wrote to apply to b12. the way they want you to apply is kind of clever - instead of emailing a resume you have to write a tiny script that posts your application to their endpoint, and run it from a ci pipeline so they can see the run logs.

the actual work happens in src/submit.py. it reads my name/email/resume link from environment variables (the workflow sets them), grabs the current utc timestamp with millisecond precision and a Z suffix, builds the json payload, sorts the keys alphabetically and strips all the whitespace out, encodes it as utf-8 bytes, and then hmac-sha256-signs those exact bytes with the secret b12 published (hello-there-from-b12). the signature goes in an x-signature-256 header. then it posts to https://b12.io/apply/submission and prints whatever receipt comes back.

didn't bother with the requests library, just used urllib from the stdlib. no requirements file needed for the actual submission, only pytest for the tests.

to run it: open the actions tab on github, find "submit b12 application", click run workflow. there's a little form with name/email/resume_link defaults filled in - tweak them if needed and hit the green button. when it finishes, click into the run, expand the submit application step, and scroll down. the receipt is printed inside a big = = = banner so it's hard to miss. copy that string and paste it into b12's confirmation form on their site. done.

there are tests in tests/test_submit.py too. they take the worked example b12 gave in their spec (the one with the timestamp 2026-01-06T16:59:37.571Z and digest c5db257a56e3c258ec1162459c9a295280871269f4cf70146d2c9f1b52671d45) and verify our canonical_body + sign functions produce that exact hex string. the submit workflow runs the tests first - if they ever break, the submission never happens, which is the whole point. there's also a separate test.yml workflow that runs on every push, just so the green check stays visible on the repo.

if you want to run the tests locally just pip install pytest and run pytest -q from the repo root. takes like 30ms.

one detail i liked - repository_link and action_run_link in the payload get auto-populated from github's context variables (github.server_url, github.repository, github.run_id), so the action_run_link in the post body always points to the exact ci run that did the submission. that felt important since b12 explicitly wants to click through and confirm the run actually happened.

if the script fails (network error, signature mismatch, b12 says no) it exits non-zero and the whole workflow goes red. if it succeeds the workflow goes green and the receipt is in the logs.

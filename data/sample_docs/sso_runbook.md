# SSO Runbook (AUTH-04)

## Symptoms
Users may see HTTP 401 responses after an SSO provider change, especially if the redirect URI or client secret was rotated.

## Probable cause
Mismatch between the callback URL registered in the identity provider and the value configured in our auth service.

## Resolution steps
1. Confirm the latest auth deployment completed successfully.
2. Validate the callback URL in the SSO provider admin console matches `https://app.example.com/auth/callback`.
3. Rotate and sync webhook signing secrets if the provider requires paired updates.
4. Review incident history for similar login failures in the last 7 days.

## Escalation
Escalate to the Identity platform team if multiple regions are impacted.

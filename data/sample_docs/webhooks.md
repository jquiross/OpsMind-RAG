# Webhook signing secrets

## Rotating secrets
1. Generate a new signing secret in the admin API settings.
2. Update the secret in the receiving service configuration.
3. Deliver a test event and verify signature validation passes.
4. Deprecate the old secret after a safe overlap window (recommended 24h).

## Common failures
- Clock skew between systems causing signature mismatch.
- Trailing newline differences in payload serialization.

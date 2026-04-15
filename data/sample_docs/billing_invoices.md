# Invoice generation delays

## Checks
- Verify the billing job queue depth in the operations dashboard.
- Confirm payment gateway connectivity and API rate limits.
- Look for stuck batch jobs referencing large tenants.

## Mitigation
Retry failed jobs after clearing rate limit errors. If delays persist, scale workers for the billing namespace.

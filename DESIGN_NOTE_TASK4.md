# Task 4 — Design Note

## Failure modes

The solution can fail in three main ways in production. First, the external LLM API can become unavailable, rate-limited, or return malformed output. This is relevant because both Task 1 and Task 2 depend on an external generative model. Detection should include API error logging, request latency and error-rate metrics, and alerts for repeated failures. Mitigation should include bounded retries with backoff, clear error handling, and returning a safe failure message rather than presenting an incomplete triage or account brief as valid. Structured output validation should also reject malformed responses before they reach a user.

Second, the model can produce a plausible but incorrect classification or summary. For example, a ticket can be assigned to the wrong product area, or an account brief can miss an important risk. This is harder to detect than an API failure because the request technically succeeds. The evaluation harness in Task 3 provides regression checks for required fields, classifications, summary constraints, and ticket-quote grounding. In production, these checks should be extended with sampled human review, quality monitoring, and a growing regression suite based on real failure cases. High-risk outputs should be routed for human review rather than treated as authoritative.

Third, the underlying data can be missing, stale, inconsistent, or incomplete. An unknown account ID or missing ticket should not cause the application to silently invent information. The current design validates account lookup and checks ticket references and verbatim quotes for risks. Production monitoring should track missing-record rates and validation failures, while the application should clearly report when source data is insufficient.

## Latency vs quality

A concrete trade-off is using a capable generative model with structured output and knowledge-base context instead of relying only on simple keyword rules. This increases response time and API dependency, but it produces more useful reasoning, classifications, and account-health recommendations.

If latency were the hard constraint, I would introduce a two-stage approach. A lightweight deterministic layer could handle obvious cases such as account lookups, required-field validation, and simple routing signals. Only ambiguous or high-value cases would be sent to the LLM. I would also stream responses where appropriate for user-facing workflows. The current Task 2 UI demonstrates streaming generation, which improves perceived responsiveness even when the complete response still requires model processing.

## Data sensitivity

Ticket and account data may contain personally identifiable or commercially sensitive information. The design should therefore minimize the data sent to an external model. Only fields required for the requested task should be included in the prompt, rather than sending complete database records by default. Sensitive fields that are not needed for classification or summarization should be redacted or omitted.

API credentials must never be included in source code or committed to Git. The project uses environment variables for the Gemini API key, with `.env` kept out of version control and `.env.example` documenting the required variable. Production deployments should use a secrets manager or equivalent secure configuration mechanism. Logs should also avoid recording raw ticket bodies, account records, API keys, or other unnecessary sensitive content.

## Scaling

At 10× the ticket volume, the first pressure point would likely be external LLM API quotas, rate limits, and cost rather than the local JSON processing. If every incoming ticket triggers a model request, concurrent traffic can quickly exceed request limits and increase latency.

The mitigation is to decouple ingestion from processing with a queue, use bounded worker concurrency, retry transient failures with backoff, and monitor queue depth and processing latency. Deterministic validation and routing can happen before expensive model calls. Frequently reused knowledge-base content can also be cached or indexed instead of repeatedly processing the same files.

For Task 2, account-health generation should similarly be cached where appropriate and refreshed when relevant account or ticket data changes. As volume grows, the JSON files used for the assignment should be replaced with a database or service layer with indexed account and ticket lookups. This keeps the application responsive while allowing model calls to scale independently.

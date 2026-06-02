# Issue Contract

Private GitHub issues are the durable training queue.

## Title

```text
요청: <wakeword>
```

Example:

```text
요청: 자비스
```

The title is human-readable. Automation must use the JSON payload in the body as the source of truth.

## Labels

Required lifecycle labels:

- `queued`
- `ready-to-train`
- `training`
- `published`
- `failed`
- `rejected`

Optional labels:

- `needs-review`
- `retryable`
- `metrics-warning`
- `experimental`

## Body Format

The issue body must contain one fenced JSON block.

```json
{
  "schema_version": 1,
  "source": "threads",
  "threads_post_id": "string",
  "threads_reply_id": "string",
  "requester_username": "string",
  "requester_id_hash": "string",
  "raw_phrase": "자비스",
  "normalized_phrase": "자비스",
  "language": "ko",
  "artifact_slug": "ko_jabeuseu_a1b2c3d4",
  "distribution_repo": "UnripePlum/korean-wakeword",
  "created_at": "2026-06-02T00:00:00Z"
}
```

## Required Fields

- `schema_version`: integer, currently `1`.
- `source`: must be `threads`.
- `threads_post_id`: source Threads post ID.
- `threads_reply_id`: source Threads reply ID and idempotency key.
- `requester_username`: display username for status comments.
- `raw_phrase`: original requested phrase after trimming.
- `normalized_phrase`: normalized Korean phrase.
- `language`: must be `ko`.
- `artifact_slug`: deterministic ASCII file stem.
- `distribution_repo`: must be `UnripePlum/korean-wakeword`.
- `created_at`: UTC ISO 8601 timestamp.

## Privacy Fields

If a stable requester ID is needed, store only `requester_id_hash`, not a raw platform account ID.

## Validation Rules

Automation must reject the payload if:

- JSON is missing or malformed;
- `schema_version` is unsupported;
- `source` is not `threads`;
- `language` is not `ko`;
- title does not start with `요청:`;
- `artifact_slug` does not match the locally recomputed slug;
- `threads_reply_id` was already processed;
- `distribution_repo` is not the expected public repository.

## Idempotency

`threads_reply_id` is the primary idempotency key.

If the bridge sees the same reply again, it should update the existing issue instead of creating a new one.

If the runner sees an issue already labeled `published`, it must exit without retraining.


# Threads Intake

## Accepted Pattern

Only comments matching this pattern create wakeword jobs:

```text
요청: <wakeword>
```

Parser:

```text
^\s*요청:\s*(.+?)\s*$
```

Examples:

```text
요청: 자비스
요청: 안녕 하늘
```

## Intake Steps

1. Fetch replies for the configured Threads request post.
2. Ignore replies without `요청:`.
3. Normalize the phrase.
4. Validate requester eligibility.
5. Validate phrase safety and length.
6. Compute artifact slug.
7. Check for an existing issue with the same `threads_reply_id`.
8. Create or update a private issue.
9. Add `queued`.
10. Add `ready-to-train` only if validation passes.
11. Reply on Threads with accepted or rejected status.

## Requester Eligibility

The product goal is to accept requests from followers. If direct follower verification is not available or unreliable, the MVP should use one of these policies:

- maintainer allowlist;
- approved commenter list;
- manual review label;
- exported follower list.

The implementation should isolate this logic in `requester_policy.py` so it can be replaced later.

## Rejection Reasons

Machine-readable rejection codes:

- `missing_request_prefix`
- `empty_phrase`
- `phrase_too_long`
- `unsafe_characters`
- `url_not_allowed`
- `not_eligible`
- `duplicate_request`

## Status Replies

Accepted:

```text
접수됨: 자비스 모델 학습을 시작합니다.
```

Rejected:

```text
반려됨: 요청 형식을 확인해 주세요. 예: 요청: 자비스
```

Completed:

```text
완료: 자비스 모델이 생성됐습니다. recall=0.91, false_accepts/hour=0.7. 모델: <url>
```

Failed:

```text
실패: 자비스 모델이 목표 성능을 통과하지 못했습니다. recall=0.72, false_accepts/hour=1.8.
```


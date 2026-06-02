# Korean Wakeword Ops Architecture

## Role

`korean-wakeword-ops` is the private control plane for Korean wakeword generation.

It receives Threads requests, turns accepted requests into private GitHub issues, runs local training on an Apple Silicon self-hosted runner, and publishes approved artifacts to the public distribution repository.

## Repositories

Private operations repository:

```text
UnripePlum/korean-wakeword-ops
```

Public distribution repository:

```text
UnripePlum/korean-wakeword
```

## Flow

```text
Threads reply
  "요청: 자비스"
      |
      v
threads_bridge
  - parse request
  - validate requester
  - normalize phrase
  - compute artifact slug
  - deduplicate by Threads reply ID
      |
      v
private GitHub issue
  title: "요청: 자비스"
  labels: queued, ready-to-train
      |
      v
GitHub Actions
  trigger: issues.labeled
  runner: [self-hosted, macOS, ARM64, wakeword-trainer]
      |
      v
training wrapper
  - validate issue payload
  - call Korean trainer
  - collect metrics
  - apply metrics gate
      |
      v
publisher
  - copy .json/.tflite
  - update public manifest
  - push to UnripePlum/korean-wakeword
      |
      v
status mirror
  - comment on private issue
  - reply on Threads
```

## Issue Contract

Issue title:

```text
요청: 자비스
```

Issue labels:

- `queued`
- `ready-to-train`
- `training`
- `published`
- `failed`
- `rejected`

Issue body JSON:

```json
{
  "schema_version": 1,
  "source": "threads",
  "threads_post_id": "string",
  "threads_reply_id": "string",
  "requester_username": "string",
  "raw_phrase": "자비스",
  "normalized_phrase": "자비스",
  "language": "ko",
  "artifact_slug": "ko_jabeuseu_a1b2c3d4",
  "distribution_repo": "UnripePlum/korean-wakeword",
  "created_at": "2026-06-02T00:00:00Z"
}
```

The title is for humans. The JSON body is the machine contract.

## Training Trigger

Workflow event:

```yaml
on:
  issues:
    types: [labeled]
```

Job condition:

```yaml
if: github.event.label.name == 'ready-to-train' && startsWith(github.event.issue.title, '요청:')
```

Runner:

```yaml
runs-on: [self-hosted, macOS, ARM64, wakeword-trainer]
```

## Publishing Contract

The ops workflow publishes only finished artifacts to the public repository:

```text
microWakeWordsKorean/<artifact_slug>.json
microWakeWordsKorean/<artifact_slug>.tflite
wake_word_manifest.json
```

Training logs, caches, private issue metadata, and raw source notes stay private.


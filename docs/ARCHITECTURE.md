# Prod Architecture

## Role

`UnripePlum/korean-wakeword` is the public production repository.

It is the public request queue, source-visible project home, model artifact catalog, and user-facing documentation site for Korean wakeword models. It must not run private training jobs and must not own a self-hosted runner.

## System Boundary

![System boundary](diagrams/system-boundary.svg)

Source: [system-boundary.mmd](diagrams/system-boundary.mmd)

Public issues are visible and editable by users. Training still starts only after a trusted actor adds `ready-to-train`.

## Internal Architecture

![Internal architecture](diagrams/internal-architecture.svg)

Source: [internal-architecture.mmd](diagrams/internal-architecture.mmd)

## External Interfaces

### Request Issue

Issue title:

```text
요청: <wakeword>
```

Collector-created issue body:

```json
{
  "schema_version": 1,
  "source": "threads",
  "collector_request_id": "req_20260602_a1b2c3d4",
  "raw_phrase": "자비스",
  "normalized_phrase": "자비스",
  "language": "ko",
  "artifact_slug": "jarvis",
  "created_at": "2026-06-02T00:00:00Z"
}
```

GitHub-created issues may omit the JSON body. In that case, the trainer derives the phrase from the title only after `ready-to-train` is added by a maintainer or trusted automation.

Request validation:

- normalized Korean wakeword length is at most 8 Hangul syllable characters;
- whitespace is normalized before counting;
- requests over the limit must be rejected or edited before `ready-to-train`.

### Labels

- `queued`: request is visible in the public queue.
- `ready-to-train`: trusted execution gate.
- `training`: trainer claimed the request.
- `published`: artifacts were committed and manifest was updated.
- `failed`: training or quality gate failed.
- `rejected`: request is invalid or not allowed.
- `retryable`: request can be retried by a trusted actor.

### Artifact Paths

```text
<artifact_slug>/<generation_start_date>/<artifact_slug>.json
<artifact_slug>/<generation_start_date>/<artifact_slug>.tflite
wake_word_manifest.json
```

Example:

```text
jarvis/2026-06-02/jarvis.json
jarvis/2026-06-02/jarvis.tflite
```

`artifact_slug` is the English-safe wakeword folder name derived from the Korean phrase, for example `jarvis` or `nukjuk`. It must be lowercase ASCII and safe as a Git path segment.

`generation_start_date` is the date when trainer generation starts, formatted as `YYYY-MM-DD`.

### Model JSON

The model JSON must include `trainer_version` and public-safe TTS generation metadata.

Recommended shape:

```json
{
  "schema_version": 1,
  "wakeword": {
    "display": "자비스",
    "slug": "jarvis",
    "language": "ko"
  },
  "artifact": {
    "generation_start_date": "2026-06-02",
    "model_path": "jarvis/2026-06-02/jarvis.tflite",
    "json_path": "jarvis/2026-06-02/jarvis.json"
  },
  "trainer": {
    "trainer_version": "0.1.0",
    "source": "UnripePlum/korean-wakeword-trainer"
  },
  "data_generation": {
    "tts_provider": "qwen",
    "tts_model": "qwen-tts",
    "positive_sample_count": 240,
    "voice_variant_count": 8,
    "dataset_manifest_hash": "sha256:example"
  },
  "metrics": {
    "recall": 0.91,
    "false_accepts_per_hour": 0.7
  },
  "runtime": {
    "probability_cutoff": 0.5,
    "sliding_window_size": 5,
    "feature_step_size": 10,
    "tensor_arena_size": 22860
  },
  "request": {
    "prod_issue": 123,
    "source": "threads"
  }
}
```

## Issue State Machine

![Issue state machine](diagrams/issue-state-machine.svg)

Source: [issue-state-machine.mmd](diagrams/issue-state-machine.mmd)

## Write Permissions

![Write permissions](diagrams/write-permissions.svg)

Source: [write-permissions.mmd](diagrams/write-permissions.mmd)

Do not attach a self-hosted runner to this repository. The public repository can contain source code, validation scripts, and artifact metadata, but execution belongs to the private trainer repo.

## Parallel Work Units

- Issue queue: labels, issue template, request examples, public status wording.
- Artifact contract: JSON schema, path validator, manifest shape.
- Manifest tooling: generate `wake_word_manifest.json` from artifact folders.
- Public docs: request guide, artifact usage guide, model compatibility notes.
- Release hygiene: validation command that can run before trainer pushes artifacts.

## Non-Goals

- Threads polling.
- Follower verification.
- Local training execution.
- Qwen TTS execution or generated audio storage.
- Self-hosted runner configuration.
- Private logs, caches, or secrets.

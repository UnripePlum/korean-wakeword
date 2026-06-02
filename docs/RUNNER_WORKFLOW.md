# Runner Workflow

## Runner

The local training runner must use these labels:

```yaml
runs-on: [self-hosted, macOS, ARM64, wakeword-trainer]
```

The runner belongs only to `korean-wakeword`.

The repository is public, so the runner must rely on the trusted `ready-to-train` label boundary and validated issue payloads.

## Trigger

```yaml
on:
  issues:
    types: [labeled]
```

## Job Condition

```yaml
if: github.event.label.name == 'ready-to-train' && startsWith(github.event.issue.title, '요청:')
```

## Workflow Shape

The workflow should be thin.

It should:

1. checkout `korean-wakeword`;
2. set up Python if needed;
3. call one wrapper script;
4. upload sanitized logs only if needed.

It should not:

- embed parsing logic in YAML;
- run shell built from issue text;
- accept commands from issue comments;
- checkout or run code from public pull requests.

## Wrapper Command

```text
python scripts/training/train_ko_issue.py --event "$GITHUB_EVENT_PATH"
```

## Local Lock

Training is resource-heavy. The wrapper must acquire a local lock before invoking the trainer.

Suggested lock path:

```text
~/.korean-wakeword/locks/training.lock
```

If the lock is held:

- comment that another training job is active;
- leave the issue queued, or fail with a retryable status;
- do not run two trainer jobs concurrently.

## Environment

Required secrets or environment values:

- `GH_TOKEN`: token for worker issue updates.
- `PUBLISH_GH_TOKEN`: token scoped to publish into `UnripePlum/korean-wakeword`.
- `DISTRIBUTION_REPO`: `UnripePlum/korean-wakeword`.
- `TRAINER_ROOT`: local checkout path for the Apple Silicon trainer.

The wrapper should fail fast if required values are missing.

## State Updates

The runner should update labels in this order:

```text
ready-to-train -> training -> published
ready-to-train -> training -> failed
```

When a terminal label is added, remove `training`.

## Log Policy

Allowed in logs:

- artifact slug;
- wakeword display phrase;
- phase names;
- non-secret metrics;
- sanitized exception messages.

Forbidden in logs:

- access tokens;
- raw authorization headers;
- private platform IDs when not necessary;
- full local cache paths containing secrets.

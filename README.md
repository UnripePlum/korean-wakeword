# Korean Wakeword

Public prod repository for Korean micro wake word models.

This repository owns:

- public README and user-facing docs;
- published Korean wakeword model artifacts;
- `wake_word_manifest.json`;
- manifest generation/validation code;
- open-source project code that is safe to publish.

It does not own:

- Threads tokens;
- requester eligibility state;
- self-hosted runner registration;
- local training secrets;
- private training issues.

Related repositories:

- `UnripePlum/korean-wakeword-request-collector`: private Threads request collector.
- `UnripePlum/korean-wakeword-trainer`: private training runner and execution queue.

## Request Flow

Users request a wakeword on Threads:

```text
요청: 자비스
```

The private collector receives the request, the private trainer generates the model, and finished artifacts are committed here.

## Published Files

```text
wakeword-ko/<artifact_slug>.json
wakeword-ko/<artifact_slug>.tflite
wake_word_manifest.json
```

## Design Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Artifact storage contract](docs/PUBLISHING.md)
- [Security notes](docs/SECURITY.md)

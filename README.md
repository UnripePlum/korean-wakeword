# Korean Wakeword

Public prod repository for Korean micro wake word models.

This repository owns:

- public README and user-facing docs;
- public wakeword request issues;
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

Users can request a wakeword in either place:

- Threads comment;
- GitHub issue in this repository.

Use this format:

```text
요청: 자비스
```

The private collector converts Threads requests into GitHub issues here. The private trainer watches approved issues here, generates the model, and commits finished artifacts back into this repository.

## Published Files

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

## Design Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Artifact storage contract](docs/PUBLISHING.md)
- [Security notes](docs/SECURITY.md)

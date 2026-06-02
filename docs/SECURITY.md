# Security Notes

## Repository Role

This repository is public. It should contain public docs, public code, and finished model artifacts only.

## No Self-Hosted Runner

Do not attach a self-hosted runner to this repository.

Self-hosted execution belongs to:

```text
UnripePlum/korean-wakeword-trainer
```

## Public Issue Policy

Public issues here are for:

- published model bugs;
- compatibility reports;
- documentation corrections;
- artifact removal or rename requests.

Opening a public issue here must not start training.

## Secret Boundary

Do not store:

- Threads tokens;
- GitHub publishing tokens;
- self-hosted runner tokens;
- private request mappings;
- local trainer logs;
- local trainer caches.

## Related Docs

- [Architecture](ARCHITECTURE.md)
- [Artifact storage contract](PUBLISHING.md)

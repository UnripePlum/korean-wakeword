# Korean Wakeword Worker

Private worker repository for the Korean wakeword generator.

This repository owns:

- public GitHub issue queue;
- local Apple Silicon self-hosted runner workflow;
- Korean wakeword training wrapper;
- metrics extraction;
- publishing finished artifacts to `UnripePlum/korean-wakeword`;
- worker issue status updates.

The request collector repository creates issues here:

```text
https://github.com/UnripePlum/korean-wakeword-request-collector
```

Finished `.json` and `.tflite` files are published into this repository after generation passes validation.

## Branches

- `develop`: development branch for worker code and tests.
- `deploy`: deployment branch used by the self-hosted runner.

The worker keeps GitHub issue-triggered workflows on `deploy`. `deploy` is the default branch because GitHub issue events run workflows from the default branch.

## Design Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Issue contract](docs/ISSUE_CONTRACT.md)
- [Runner workflow](docs/RUNNER_WORKFLOW.md)
- [Publishing contract](docs/PUBLISHING.md)
- [Branching](docs/BRANCHING.md)
- [Security notes](docs/SECURITY.md)

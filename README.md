# Korean Wakeword Ops

Private operations repository for the Korean wakeword generator.

This repository owns:

- Threads reply intake;
- `요청:` parsing and validation;
- private GitHub issue queue;
- local Apple Silicon self-hosted runner workflow;
- Korean wakeword training wrapper;
- metrics extraction;
- publishing finished artifacts to `UnripePlum/korean-wakeword`;
- status mirroring back to Threads.

The public distribution repository is:

```text
https://github.com/UnripePlum/korean-wakeword
```

Do not put public model artifacts here unless they are temporary training outputs. Finished `.json` and `.tflite` files are published to the public distribution repository.

## Design Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Threads intake](docs/THREADS_INTAKE.md)
- [Issue contract](docs/ISSUE_CONTRACT.md)
- [Runner workflow](docs/RUNNER_WORKFLOW.md)
- [Publishing contract](docs/PUBLISHING.md)
- [Security notes](docs/SECURITY.md)

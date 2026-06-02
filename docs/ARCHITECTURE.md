# Worker Architecture

## Role

`UnripePlum/korean-wakeword` is the public issue-driven worker for Korean wakeword generation.

It does not poll Threads. The private request collector creates public-safe issues in this repository. The worker consumes those issues, trains wakeword models on the local Apple Silicon self-hosted runner, and stores finished artifacts in this same repository.

## High-Level Flow

```mermaid
flowchart TD
    A["Request collector"]

    subgraph ISSUE["Worker issue queue"]
        B1["Issue title: 요청: 자비스"]
        B2["Issue body: generation JSON"]
        B3["Label: ready-to-train"]
    end

    subgraph BRANCHES["Worker branches"]
        C1["develop<br/>implementation and tests"]
        C2["deploy<br/>active runner workflow"]
    end

    subgraph ACTIONS["GitHub Actions on deploy"]
        D1["Event: issues.labeled"]
        D2["Workflow from default branch"]
        D3["Runner: self-hosted macOS ARM64"]
    end

    subgraph TRAIN["Wakeword generation"]
        E1["Validate issue payload"]
        E2["Acquire local training lock"]
        E3["Invoke Korean trainer"]
        E4["Extract metrics"]
        E5["Apply quality gate"]
    end

    subgraph PUBLISH["Publish result"]
        F1["Copy model JSON and TFLite"]
        F2["Regenerate manifest"]
        F3["Commit artifacts to this repository"]
    end

    G["Worker issue result comment"]
    H["Published model files"]

    A --> B1 --> B2 --> B3
    C1 -->|"release merge"| C2
    B3 --> D1 --> D2 --> D3
    C2 --> D2
    D3 --> E1 --> E2 --> E3 --> E4 --> E5
    E5 --> F1 --> F2 --> F3 --> H
    E5 --> G
    F3 --> G
```

## Responsibilities

The worker owns:

- the public worker issue queue;
- wakeword generation job state;
- self-hosted runner workflow;
- training wrapper;
- metrics extraction;
- quality gate;
- artifact publication into this repository;
- worker issue comments and labels.

The worker does not own:

- Threads polling;
- Threads request parsing;
- requester eligibility checks;
- direct Threads replies.

Those belong to `UnripePlum/korean-wakeword-request-collector`.

## Branch Model

The worker always keeps development and deployment separated.

```mermaid
flowchart LR
    A["develop<br/>code changes, tests, review"] -->|"release merge"| B["deploy<br/>default branch, active issue workflow"]
    B --> C["Self-hosted runner"]
    C --> D["Wakeword generation"]
```

Rules:

- `develop` is for implementation work.
- `deploy` is the production branch for issue-triggered worker execution.
- `deploy` is the GitHub default branch so `issues.labeled` workflows run from deployed code.
- The self-hosted runner workflow must be active only from `deploy`.
- Release changes move from `develop` to `deploy` after tests and review.

## Issue Queue

Worker issues are created by the request collector.

Issue title:

```text
요청: 자비스
```

Required lifecycle labels:

- `queued`
- `ready-to-train`
- `training`
- `published`
- `failed`
- `rejected`

The worker starts only when `ready-to-train` is added.

## State Machine

```mermaid
stateDiagram-v2
    [*] --> Queued: collector creates issue
    Queued --> ReadyToTrain: collector labels accepted request
    ReadyToTrain --> Training: worker starts
    Training --> Published: metrics pass and public publish succeeds
    Training --> Failed: trainer, metrics, or publish failure
    Failed --> ReadyToTrain: manual retry
    Published --> [*]
```

Only one local training job should run at a time. The wrapper must acquire a local file lock before invoking the trainer.

## Wakeword Generation

The worker receives:

- Korean display phrase;
- normalized phrase;
- deterministic ASCII artifact slug;
- collector request ID for idempotency and status correlation;
- target publication repository.

The worker must:

- validate the issue payload again;
- recompute or verify `artifact_slug`;
- pass the Korean phrase to the trainer;
- pass the ASCII artifact slug as the output-safe name;
- extract metrics;
- publish only after the metrics gate passes.

## Publishing

Successful worker jobs publish into this repository:

```text
UnripePlum/korean-wakeword
```

Published files:

```text
microWakeWordsKorean/<artifact_slug>.json
microWakeWordsKorean/<artifact_slug>.tflite
wake_word_manifest.json
```

## Result Reporting

The worker reports results by updating the worker issue:

- label transition;
- result comment;
- artifact URLs;
- metrics;
- failure code when failed.

The request collector may read these issue updates and mirror the final status back to Threads.

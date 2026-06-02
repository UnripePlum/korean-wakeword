# Security Notes

## Main Boundary

This public repository owns the local Apple Silicon self-hosted runner workflow. Treat the runner as privileged.

The public distribution repository must not have access to the training runner. The private request collector may create issues here, but issue creation alone must not start training.

## Allowed Training Trigger

Training may run only when all conditions are true:

- event is `issues.labeled`;
- added label is `ready-to-train`;
- label was applied by the private request collector token or a maintainer;
- issue title starts with `요청:`;
- issue body JSON validates against the expected schema;
- job runs on `[self-hosted, macOS, ARM64, wakeword-trainer]`.

## Forbidden Triggers

Do not run training from:

- `pull_request`;
- `pull_request_target`;
- arbitrary `issues.opened`;
- issue comments containing commands;
- user-edited workflow files.

Public users may open issues in this repository, but public issue creation must never start local training.

## Input Handling

Threads replies and GitHub issue fields are untrusted data.

Rules:

- Do not interpolate requested wakewords into shell commands.
- Pass trainer arguments as structured argument arrays.
- Recompute or validate `artifact_slug` locally.
- Reject URLs, control characters, empty phrases, and unsafe payloads.
- Never trust the issue title as the only data source.

## Secrets

- Keep GitHub tokens in repository or environment secrets.
- Do not store Threads tokens in the worker repository; Threads status belongs to the private request collector.
- Do not write tokens to logs, issues, comments, or model artifacts.
- Scope the publishing token to `UnripePlum/korean-wakeword`.
- Prefer a dedicated local runner user on the Mac.

## Related Contracts

- [Issue contract](ISSUE_CONTRACT.md)
- [Runner workflow](RUNNER_WORKFLOW.md)
- [Publishing contract](PUBLISHING.md)
- [Branching policy](BRANCHING.md)

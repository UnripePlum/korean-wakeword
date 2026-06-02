# Publishing Contract

The public worker repository publishes finished artifacts into this same repository.

Public repository:

```text
UnripePlum/korean-wakeword
```

## Published Files

Each successful job writes:

```text
microWakeWordsKorean/<artifact_slug>.json
microWakeWordsKorean/<artifact_slug>.tflite
```

Then it regenerates:

```text
wake_word_manifest.json
```

## Commit Message

Use a machine-readable commit message:

```text
Add Korean wakeword: <normalized_phrase> (<artifact_slug>)

Source: threads
Worker-Issue: UnripePlum/korean-wakeword#<issue_number>
Metrics: recall=<value>, faph=<value>
```

## Metrics Gate

Default production thresholds:

- recall: `>= 0.85`
- false accepts per hour: `<= 1.0`
- raw positive detection rate, when available: `>= 0.80`
- raw negative detections, when available: `0`

If a job misses the gate:

- do not publish by default;
- add `failed`;
- comment metrics and failure reason on the worker issue;
- let the request collector mirror the failure back to Threads.

Experimental publication may be added later with a separate `experimental` label.

## Manifest Requirements

The model JSON should include runtime fields needed by micro wake word firmware:

- wake word display text;
- model path;
- trained language `ko`;
- probability cutoff;
- sliding window size;
- feature step size;
- tensor arena size.

The repository manifest should expose the raw GitHub URL for each model JSON.

## Conflict Handling

If pushing to the public repository fails because `main` moved:

1. fetch and rebase once;
2. regenerate manifest;
3. retry push once;
4. fail with `publish_conflict` if it still fails.

## Public Metadata

Published metadata may include:

- display phrase;
- artifact slug;
- metrics;
- model version;
- language;
- generation timestamp.

Published metadata must not include:

- Threads access tokens;
- broad-scope GitHub tokens;
- private collector payloads;
- unnecessary requester IDs;
- local filesystem paths.

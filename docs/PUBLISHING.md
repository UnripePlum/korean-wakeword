# Artifact Storage Contract

This repository stores finished Korean wakeword artifacts.

## Writer

Artifacts are written by the private trainer repository:

```text
UnripePlum/korean-wakeword-trainer
```

## Stored Files

Each successful job writes:

```text
wakeword-ko/<artifact_slug>.json
wakeword-ko/<artifact_slug>.tflite
```

Then it regenerates:

```text
wake_word_manifest.json
```

## Required Metadata

Each model JSON should include:

- Korean display wakeword;
- matching `.tflite` path;
- trained language `ko`;
- probability cutoff;
- sliding window size;
- feature step size;
- tensor arena size;
- quality metrics when available.

## Forbidden Public Data

Do not publish:

- Threads tokens;
- GitHub tokens;
- private collector payloads;
- private trainer internals beyond a public-safe reference;
- raw user audio unless explicitly intended and licensed;
- local filesystem paths;
- copied external source material.

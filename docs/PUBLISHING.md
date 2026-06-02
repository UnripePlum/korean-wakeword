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
<artifact_slug>/<generation_start_date>/<artifact_slug>.json
<artifact_slug>/<generation_start_date>/<artifact_slug>.tflite
```

Then it regenerates:

```text
wake_word_manifest.json
```

## Required Metadata

`artifact_slug` is the English-safe wakeword folder name derived from the Korean phrase, for example `jarvis` or `nukjuk`. It must be lowercase ASCII and safe as a Git path segment.

Each model JSON should include:

- Korean display wakeword;
- matching `.tflite` path;
- generation start date;
- trainer version;
- trained language `ko`;
- public-safe Qwen TTS generation metadata;
- probability cutoff;
- sliding window size;
- feature step size;
- tensor arena size;
- quality metrics when available.

`trainer_version` is required. A model JSON without `trainer_version` is invalid.

TTS metadata should identify how positive samples were generated without exposing private data:

- `data_generation.tts_provider`: `qwen`;
- `data_generation.tts_model`;
- `data_generation.positive_sample_count`;
- `data_generation.voice_variant_count`;
- `data_generation.dataset_manifest_hash`, when available.

## Forbidden Public Data

Do not publish:

- Threads tokens;
- GitHub tokens;
- private collector payloads;
- private trainer internals beyond a public-safe reference;
- raw Qwen TTS generated audio;
- Qwen TTS tokens, prompts, request logs, or private cache paths;
- raw user audio unless explicitly intended and licensed;
- local filesystem paths;
- copied external source material.

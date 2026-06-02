<div align="center">

# Korean Wakeword

**Request Korean micro wake word models through GitHub Issues.**

[![Validate](https://github.com/UnripePlum/korean-wakeword/actions/workflows/validate.yml/badge.svg)](https://github.com/UnripePlum/korean-wakeword/actions/workflows/validate.yml)
[![Manifest](https://img.shields.io/badge/manifest-wake__word__manifest.json-blue)](wake_word_manifest.json)
[![Language](https://img.shields.io/badge/language-Korean-green)](#request-rules)
[![Example](https://img.shields.io/badge/example-%EC%9A%94%EC%B2%AD%3A%EC%9E%90%EB%B9%84%EC%8A%A4-orange)](#quick-start)

[Quick Start](#quick-start) ·
[Published Layout](#published-layout) ·
[Evaluation](#evaluation) ·
[Manifest](wake_word_manifest.json) ·
[Docs](#docs) ·
[Contact](#contact)

</div>

---

Korean Wakeword is a public catalog for Korean micro wake word requests and published model artifacts. Create an issue like `요청:자비스`; after approval and generation, this repository receives a model folder plus an updated manifest.

## Quick Start

1. Open a new GitHub Issue.

   [Request a wake word](https://github.com/UnripePlum/korean-wakeword/issues/new?title=%EC%9A%94%EC%B2%AD%3A%EC%9E%90%EB%B9%84%EC%8A%A4)

2. Write the issue title or body like this:

   ```text
   요청:자비스
   ```

3. Wait for the request to be approved and generated.

4. Use the published `.tflite`, metadata JSON, or manifest entry.

## What Gets Published

When a request is processed, the generated model appears as a folder:

```text
jarvis/2026-06-02/jarvis.json
jarvis/2026-06-02/jarvis.tflite
```

The model is also indexed in:

```text
wake_word_manifest.json
```

## Request Rules

- Use Korean.
- Keep the wake word at 8 syllables or fewer.
- Use the format `요청:<wakeword>`.

## Published Layout

```text
<artifact_slug>/<generation_start_date>/<artifact_slug>.json
<artifact_slug>/<generation_start_date>/<artifact_slug>.tflite
wake_word_manifest.json
```

## Use the Manifest

`wake_word_manifest.json` is the public index of generated models. Each entry points to the model file, metadata file, runtime settings, and public-safe generation metadata.

## Evaluation

Each model metadata file may include public evaluation results:

| Field | Meaning |
| --- | --- |
| `metrics.recall` | How often the model detects the target wake word in evaluation samples. Higher is better. |
| `metrics.false_accepts_per_hour` | Estimated false wakeups per hour. Lower is better. |
| `runtime.probability_cutoff` | Suggested detection threshold for runtime use. |

Evaluation quality can vary by device, microphone, background noise, and runtime settings. Treat the metrics as a starting point, then tune the cutoff for your own environment.

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Publishing contract](docs/PUBLISHING.md)
- [Security notes](docs/SECURITY.md)

## Contact

For questions or artifact requests, email [unripeplum03@gmail.com](mailto:unripeplum03@gmail.com).

<details>
<summary>Maintainer commands</summary>

Run these before publishing artifact changes:

```sh
python -m unittest discover -s tests
python scripts/manifest/generate.py --check
```

</details>

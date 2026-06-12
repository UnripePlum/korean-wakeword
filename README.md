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
[Performance](#performance) ·
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
jarvis/2026-06-08T03-42-20Z/jarvis.json
jarvis/2026-06-08T03-42-20Z/jarvis.tflite
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
<artifact_slug>/<generation_version>/<artifact_slug>.json
<artifact_slug>/<generation_version>/<artifact_slug>.tflite
wake_word_manifest.json
```

`generation_version` is the UTC generation start timestamp, formatted as
`YYYY-MM-DDTHH-MM-SSZ`.

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

## Performance

This repository exposes public performance metrics for each published wake word using the fields below.

### Public metric definitions

| Field | Meaning | Higher is better |
| --- | --- | --- |
| `recall` | Detection rate for target wake words. Ratio of correctly detected positive samples | yes |
| `false_accepts_per_hour` | Estimated false acceptance rate per hour (FAR) | no |
| `raw_positive_detection_rate` | Raw positive detection rate before internal adjustment | yes |
| `raw_negative_total` | Total number of negative audio samples used | - |
| `raw_negative_detections` | Number of false detections on negative samples | no |
| `hard_negative_sample_count` | Number of hard-negative samples (difficult negative examples) | - |
| `probability_cutoff` | Runtime detection threshold | tune by environment |
| `training_duration_minutes` | Training duration in minutes | - |

### Public performance snapshot

The table below uses `wakeword.display` values from the manifest (human-readable names).

Sample table from `wake_word_manifest.json` metadata (latest snapshot):

| wakeword (display) | generation_version | recall | false_accepts_per_hour | probability_cutoff | training_duration_minutes |
| --- | --- | ---: | ---: | ---: | ---: |
| 개발모드 | 2026-06-08T14-00-23Z | 0.9524 | 15.79 | 1.00 | 41.37 |

### Performance graph

![Latest performance snapshot](docs/performance-latest.svg)
```text
recall (higher is better):        ████████████████████████████████████████ 0.9524
false_accepts/hour (lower better):███████████████████████                 15.79
```

This chart shows the same values in one view using original metrics from the manifest:

- Recall (blue): higher is better.
- False accepts/hour (teal): lower is better.

### How to read and compare

- Compare only within the same dataset, runtime configuration, and detection threshold.
- Always inspect `artifact.generation_version`, `runtime.*`, and `data_generation.*` together when comparing numbers.
- A clear changelog-style format is `old -> new` per wake word (for example, recall and `false_accepts_per_hour`).
- `probability_cutoff` may need adjustment based on environmental noise, mic quality, and sliding window settings.

### Reproducibility checklist

To reproduce results:

- Keep the generated `generation_version` and metadata fields (`artifact`, `runtime`, `artifact_contract`) fixed.
- Use the same audio corpus and the same hard-negative sample set.
- Use the same evaluation script and `probability_cutoff`.
- Update `wake_word_manifest.json` before release.

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

## Performance

<!-- KWW:PERFORMANCE_TABLE_START -->
| Wakeword | Slug | Generation | Recall | False accepts/hour | Cutoff | Training |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 변신 | `byeonsin` | `2026-06-08T16-10-37Z` | 86.5% | 15.42 | 1 | 42.68 min |
| 개발모드 | `gaebalmodeu` | `2026-06-08T14-00-23Z` | 95.2% | 15.793 | 1 | 41.37 min |
| 게임모드 | `geimmodeu` | `2026-06-12T12-11-32Z` | 92.3% | 15.995 | 1 | 71.98 min |
<!-- KWW:PERFORMANCE_TABLE_END -->

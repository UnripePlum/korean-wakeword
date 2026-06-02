# Korean Wakeword

Korean Wakeword is a public catalog for Korean micro wake word models.

If you want a new wake word model, create a GitHub Issue in this repository using the request format below. When the request is accepted and processed, the generated model files are published as a folder in this repo.

## Quick Start

1. Open a new GitHub Issue.
2. Write the request in this format:

```text
요청:자비스
```

3. After the model is generated, a model folder is added:

```text
jarvis/2026-06-02/jarvis.json
jarvis/2026-06-02/jarvis.tflite
```

4. The model also appears in:

```text
wake_word_manifest.json
```

## Request Rules

- Use Korean.
- Keep the wake word at 8 syllables or fewer.
- Use the issue title or body format `요청:<wakeword>`.

## Published File Layout

```text
<artifact_slug>/<generation_start_date>/<artifact_slug>.json
<artifact_slug>/<generation_start_date>/<artifact_slug>.tflite
wake_word_manifest.json
```

## For Maintainers

```sh
python -m unittest discover -s tests
python scripts/manifest/generate.py --check
```

More details:

- [Architecture](docs/ARCHITECTURE.md)
- [Publishing](docs/PUBLISHING.md)
- [Security](docs/SECURITY.md)

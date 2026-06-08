from __future__ import annotations

import copy
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


MANIFEST_NAME = "wake_word_manifest.json"
MANIFEST_SCHEMA_VERSION = 1
MODEL_SCHEMA_VERSION = 1

RESERVED_ROOT_DIRECTORIES = {
    ".git",
    ".github",
    "__pycache__",
    "docs",
    "scripts",
    "tests",
}

ARTIFACT_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
GENERATION_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
GENERATION_VERSION_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}(?:T\d{2}-\d{2}-\d{2}Z)?$"
)

FORBIDDEN_PUBLIC_KEY_PARTS = (
    "token",
    "secret",
    "password",
    "authorization",
    "api_key",
    "apikey",
    "private_key",
    "private_cache",
    "cache_path",
    "request_log",
    "raw_audio",
    "prompt",
)

LOCAL_PATH_RE = re.compile(r"(^/)|(^[A-Za-z]:\\)|(/Users/)|(/home/)|(/tmp/)|(\\\\)")


class ManifestError(ValueError):
    """Raised when artifact metadata cannot be published safely."""


def build_manifest(repo_root: Path | str) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    models = []

    for artifact in _discover_artifacts(root):
        metadata = _load_json(artifact["json_file"])
        _validate_model_metadata(
            metadata=metadata,
            artifact_slug=artifact["slug"],
            generation_start_date=artifact["date"],
            generation_version=artifact["version"],
            expected_json_path=artifact["json_rel"],
            expected_model_path=artifact["model_rel"],
        )
        models.append(copy.deepcopy(metadata))

    models.sort(
        key=lambda model: (
            model["wakeword"]["slug"],
            model["artifact"].get("generation_started_at")
            or model["artifact"].get("generation_version")
            or model["artifact"]["generation_start_date"],
            model["artifact"].get("generation_version", ""),
        )
    )

    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "model_count": len(models),
        "models": models,
    }


def write_manifest(repo_root: Path | str) -> Path:
    root = Path(repo_root).resolve()
    manifest_path = root / MANIFEST_NAME
    manifest_path.write_text(render_manifest(build_manifest(root)), encoding="utf-8")
    return manifest_path


def check_manifest(repo_root: Path | str) -> None:
    root = Path(repo_root).resolve()
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.is_file():
        raise ManifestError(f"missing {MANIFEST_NAME}; run manifest generation with --write")

    current = _load_json(manifest_path)
    expected = build_manifest(root)
    if current != expected:
        raise ManifestError(f"{MANIFEST_NAME} is out of date; run manifest generation with --write")
    if manifest_path.read_text(encoding="utf-8") != render_manifest(expected):
        raise ManifestError(f"{MANIFEST_NAME} is out of date; run manifest generation with --write")


def render_manifest(manifest: dict[str, Any]) -> str:
    return json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _discover_artifacts(root: Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []

    for slug_dir in sorted(root.iterdir(), key=lambda path: path.name):
        if not slug_dir.is_dir() or slug_dir.name in RESERVED_ROOT_DIRECTORIES:
            continue
        if slug_dir.name.startswith("."):
            continue

        for version_dir in sorted(slug_dir.iterdir(), key=lambda path: path.name):
            if not version_dir.is_dir():
                continue
            if not GENERATION_VERSION_RE.fullmatch(version_dir.name):
                if _looks_like_artifact_directory(slug_dir.name, version_dir):
                    _validate_artifact_slug(slug_dir.name)
                    _validate_generation_version(version_dir.name)
                continue

            _validate_artifact_slug(slug_dir.name)
            generation_start_date = _generation_date_from_version(version_dir.name)

            json_file = version_dir / f"{slug_dir.name}.json"
            model_file = version_dir / f"{slug_dir.name}.tflite"
            json_rel = _repo_relative_path(root, json_file)
            model_rel = _repo_relative_path(root, model_file)

            if not json_file.is_file():
                raise ManifestError(f"missing model JSON file: {json_rel}")
            if not model_file.is_file():
                raise ManifestError(f"missing model file: {model_rel}")
            if model_file.stat().st_size == 0:
                raise ManifestError(f"empty model file: {model_rel}")

            artifacts.append(
                {
                    "slug": slug_dir.name,
                    "date": generation_start_date,
                    "version": version_dir.name,
                    "json_file": json_file,
                    "json_rel": json_rel,
                    "model_rel": model_rel,
                }
            )

    return artifacts


def _looks_like_artifact_directory(slug: str, path: Path) -> bool:
    return (
        (path / f"{slug}.json").exists()
        or (path / f"{slug}.tflite").exists()
        or any(
            child.suffix in {".json", ".tflite"}
            for child in path.iterdir()
            if child.is_file()
        )
    )


def _validate_model_metadata(
    *,
    metadata: Any,
    artifact_slug: str,
    generation_start_date: str,
    generation_version: str,
    expected_json_path: str,
    expected_model_path: str,
) -> None:
    if not isinstance(metadata, dict):
        raise ManifestError("model JSON root must be an object")

    _scan_public_safe(metadata)

    schema_version = _require_int(metadata, "schema_version")
    if schema_version != MODEL_SCHEMA_VERSION:
        raise ManifestError(f"schema_version must be {MODEL_SCHEMA_VERSION}")

    display = _require_string(metadata, "wakeword.display")
    _validate_korean_wakeword(display)

    slug = _require_string(metadata, "wakeword.slug")
    if slug != artifact_slug:
        raise ManifestError(
            f"wakeword.slug must match artifact_slug {artifact_slug!r}; got {slug!r}"
        )
    _validate_artifact_slug(slug)

    language = _require_string(metadata, "wakeword.language")
    if language != "ko":
        raise ManifestError("wakeword.language must be 'ko'")

    metadata_date = _require_string(metadata, "artifact.generation_start_date")
    if metadata_date != generation_start_date:
        raise ManifestError(
            "artifact.generation_start_date must match artifact directory date "
            f"{generation_start_date!r}; got {metadata_date!r}"
        )
    _validate_generation_start_date(metadata_date)
    metadata_version = _optional_string(metadata, "artifact.generation_version")
    metadata_started_at = _optional_string(metadata, "artifact.generation_started_at")
    if generation_version != generation_start_date:
        if metadata_version != generation_version:
            raise ManifestError(
                "artifact.generation_version must match artifact directory "
                f"{generation_version!r}; got {metadata_version!r}"
            )
        if metadata_started_at is None:
            raise ManifestError(
                "artifact.generation_started_at is required for timestamped artifacts"
            )
    if metadata_version is not None:
        if metadata_version != generation_version:
            raise ManifestError(
                "artifact.generation_version must match artifact directory "
                f"{generation_version!r}; got {metadata_version!r}"
            )
        _validate_generation_version(metadata_version)
    if metadata_started_at is not None:
        _validate_generation_started_at(
            metadata_started_at,
            generation_start_date=generation_start_date,
            generation_version=generation_version,
        )

    json_path = _require_string(metadata, "artifact.json_path")
    model_path = _require_string(metadata, "artifact.model_path")
    _validate_relative_posix_path(json_path, "artifact.json_path")
    _validate_relative_posix_path(model_path, "artifact.model_path")
    if json_path != expected_json_path:
        raise ManifestError(
            f"artifact.json_path must be {expected_json_path!r}; got {json_path!r}"
        )
    if model_path != expected_model_path:
        raise ManifestError(
            f"artifact.model_path must be {expected_model_path!r}; got {model_path!r}"
        )

    _require_string(metadata, "trainer.trainer_version")

    provider = _require_string(metadata, "data_generation.tts_provider")
    if provider != "qwen":
        raise ManifestError("data_generation.tts_provider must be 'qwen'")
    _require_string(metadata, "data_generation.tts_model")
    _require_positive_int(metadata, "data_generation.positive_sample_count")
    _require_positive_int(metadata, "data_generation.voice_variant_count")
    dataset_hash = _optional_string(metadata, "data_generation.dataset_manifest_hash")
    if dataset_hash is not None and not dataset_hash.startswith("sha256:"):
        raise ManifestError("data_generation.dataset_manifest_hash must start with 'sha256:'")

    probability_cutoff = _require_number(metadata, "runtime.probability_cutoff")
    if probability_cutoff < 0 or probability_cutoff > 1:
        raise ManifestError("runtime.probability_cutoff must be between 0 and 1")
    _require_positive_int(metadata, "runtime.sliding_window_size")
    _require_positive_int(metadata, "runtime.feature_step_size")
    _require_positive_int(metadata, "runtime.tensor_arena_size")

    metrics = _optional_mapping(metadata, "metrics")
    if metrics is not None:
        recall = _optional_number(metadata, "metrics.recall")
        if recall is not None and (recall < 0 or recall > 1):
            raise ManifestError("metrics.recall must be between 0 and 1")
        false_accepts = _optional_number(metadata, "metrics.false_accepts_per_hour")
        if false_accepts is not None and false_accepts < 0:
            raise ManifestError("metrics.false_accepts_per_hour must be non-negative")


def _validate_artifact_slug(slug: str) -> None:
    if not ARTIFACT_SLUG_RE.fullmatch(slug):
        raise ManifestError(
            "invalid artifact_slug: must be lowercase ASCII and safe as a path segment"
        )


def _validate_generation_start_date(value: str) -> None:
    if not GENERATION_DATE_RE.fullmatch(value):
        raise ManifestError("generation_start_date must use YYYY-MM-DD")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ManifestError(f"invalid generation_start_date: {value}") from exc


def _generation_date_from_version(value: str) -> str:
    _validate_generation_version(value)
    return value[:10]


def _validate_generation_version(value: str) -> None:
    if not GENERATION_VERSION_RE.fullmatch(value):
        raise ManifestError(
            "generation_version must use YYYY-MM-DD or YYYY-MM-DDTHH-MM-SSZ"
        )
    if GENERATION_DATE_RE.fullmatch(value):
        _validate_generation_start_date(value)
        return
    try:
        datetime.strptime(value, "%Y-%m-%dT%H-%M-%SZ")
    except ValueError as exc:
        raise ManifestError(f"invalid generation_version: {value}") from exc


def _validate_generation_started_at(
    value: str,
    *,
    generation_start_date: str,
    generation_version: str,
) -> None:
    if not value.endswith("Z"):
        raise ManifestError("generation_started_at must be a UTC timestamp ending in Z")
    try:
        started_at = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ManifestError(f"invalid generation_started_at: {value}") from exc
    if started_at.tzinfo is None:
        raise ManifestError("generation_started_at must include UTC timezone")
    started_at = started_at.astimezone(timezone.utc).replace(microsecond=0)
    if started_at.date().isoformat() != generation_start_date:
        raise ManifestError(
            "generation_started_at date must match generation_start_date"
        )
    expected_version = started_at.strftime("%Y-%m-%dT%H-%M-%SZ")
    if generation_version != generation_start_date and expected_version != generation_version:
        raise ManifestError(
            "generation_started_at must match artifact.generation_version"
        )


def _validate_korean_wakeword(value: str) -> None:
    normalized = " ".join(value.split())
    if not normalized:
        raise ManifestError("wakeword.display must be non-empty")

    syllables = [character for character in normalized if character != " "]
    for character in syllables:
        if not ("\uac00" <= character <= "\ud7a3"):
            raise ManifestError("wakeword.display must contain only Hangul syllables")
    if len(syllables) > 8:
        raise ManifestError("wakeword.display must be at most 8 Hangul syllables")


def _validate_relative_posix_path(value: str, field: str) -> None:
    if "\\" in value:
        raise ManifestError(f"{field} must use POSIX '/' path separators")

    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts:
        raise ManifestError(f"{field} must be a relative path")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ManifestError(f"{field} must not contain empty, '.', or '..' segments")


def _scan_public_safe(value: Any, path: str = "") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ManifestError("model JSON keys must be strings")
            child_path = f"{path}.{key}" if path else key
            lowered_key = key.lower().replace("-", "_")
            if any(part in lowered_key for part in FORBIDDEN_PUBLIC_KEY_PARTS):
                raise ManifestError(f"forbidden public metadata key: {child_path}")
            _scan_public_safe(child, child_path)
        return

    if isinstance(value, list):
        for index, child in enumerate(value):
            _scan_public_safe(child, f"{path}[{index}]")
        return

    if isinstance(value, str) and _looks_like_local_path(value):
        raise ManifestError(f"forbidden local filesystem path in metadata: {path}")


def _looks_like_local_path(value: str) -> bool:
    return bool(LOCAL_PATH_RE.search(value) or value.startswith("file:"))


def _load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise ManifestError(f"invalid JSON: {_safe_path(path)}: {exc}") from exc


def _require_string(data: dict[str, Any], path: str) -> str:
    value = _get_required(data, path)
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{path} must be a non-empty string")
    return value


def _optional_string(data: dict[str, Any], path: str) -> str | None:
    value = _get_optional(data, path)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{path} must be a non-empty string")
    return value


def _require_int(data: dict[str, Any], path: str) -> int:
    value = _get_required(data, path)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ManifestError(f"{path} must be an integer")
    return value


def _require_positive_int(data: dict[str, Any], path: str) -> int:
    value = _require_int(data, path)
    if value <= 0:
        raise ManifestError(f"{path} must be a positive integer")
    return value


def _require_number(data: dict[str, Any], path: str) -> float:
    value = _get_required(data, path)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ManifestError(f"{path} must be a number")
    return float(value)


def _optional_number(data: dict[str, Any], path: str) -> float | None:
    value = _get_optional(data, path)
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ManifestError(f"{path} must be a number")
    return float(value)


def _optional_mapping(data: dict[str, Any], path: str) -> dict[str, Any] | None:
    value = _get_optional(data, path)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ManifestError(f"{path} must be an object")
    return value


def _get_required(data: dict[str, Any], path: str) -> Any:
    value = _get_optional(data, path)
    if value is None:
        raise ManifestError(f"missing {path}")
    return value


def _get_optional(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            raise ManifestError(f"{path} must be nested under an object")
        if part not in current:
            return None
        current = current[part]
    return current


def _repo_relative_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _safe_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()

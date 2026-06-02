import json
import tempfile
import unittest
from pathlib import Path

from scripts.manifest.core import (
    ManifestError,
    build_manifest,
    check_manifest,
    write_manifest,
)


def valid_model_metadata(slug="jarvis", display="자비스", date="2026-06-02"):
    return {
        "schema_version": 1,
        "wakeword": {
            "display": display,
            "slug": slug,
            "language": "ko",
        },
        "artifact": {
            "generation_start_date": date,
            "model_path": f"{slug}/{date}/{slug}.tflite",
            "json_path": f"{slug}/{date}/{slug}.json",
        },
        "trainer": {
            "trainer_version": "0.1.0",
            "source": "UnripePlum/korean-wakeword-trainer",
        },
        "data_generation": {
            "tts_provider": "qwen",
            "tts_model": "qwen-tts",
            "positive_sample_count": 240,
            "voice_variant_count": 8,
            "dataset_manifest_hash": "sha256:example",
        },
        "metrics": {
            "recall": 0.91,
            "false_accepts_per_hour": 0.7,
        },
        "runtime": {
            "probability_cutoff": 0.5,
            "sliding_window_size": 5,
            "feature_step_size": 10,
            "tensor_arena_size": 22860,
        },
        "request": {
            "prod_issue": 123,
            "source": "threads",
        },
    }


def write_artifact(root, slug="jarvis", display="자비스", date="2026-06-02", metadata=None):
    artifact_dir = Path(root) / slug / date
    artifact_dir.mkdir(parents=True)
    data = (
        metadata
        if metadata is not None
        else valid_model_metadata(slug=slug, display=display, date=date)
    )
    (artifact_dir / f"{slug}.json").write_text(
        json.dumps(data, ensure_ascii=False), encoding="utf-8"
    )
    (artifact_dir / f"{slug}.tflite").write_bytes(b"model")


class ManifestTests(unittest.TestCase):
    def test_builds_deterministic_manifest_from_valid_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_artifact(tmp, slug="nukjuk", display="녹즙", date="2026-06-03")
            write_artifact(tmp, slug="jarvis", display="자비스", date="2026-06-02")

            manifest = build_manifest(Path(tmp))

            self.assertEqual(manifest["schema_version"], 1)
            self.assertEqual(manifest["model_count"], 2)
            self.assertEqual(
                [model["wakeword"]["slug"] for model in manifest["models"]],
                ["jarvis", "nukjuk"],
            )
            self.assertEqual(
                manifest["models"][0]["artifact"]["model_path"],
                "jarvis/2026-06-02/jarvis.tflite",
            )

    def test_write_manifest_outputs_canonical_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_artifact(tmp)

            write_manifest(Path(tmp))
            manifest_path = Path(tmp) / "wake_word_manifest.json"

            written = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(written["model_count"], 1)
            self.assertTrue(manifest_path.read_text(encoding="utf-8").endswith("\n"))

    def test_rejects_missing_trainer_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata = valid_model_metadata()
            metadata["trainer"].pop("trainer_version")
            write_artifact(tmp, metadata=metadata)

            with self.assertRaisesRegex(ManifestError, "trainer.trainer_version"):
                build_manifest(Path(tmp))

    def test_rejects_slug_that_is_not_lowercase_ascii_path_segment(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata = valid_model_metadata(slug="Jarvis")
            write_artifact(tmp, slug="Jarvis", metadata=metadata)

            with self.assertRaisesRegex(ManifestError, "invalid artifact_slug"):
                build_manifest(Path(tmp))

    def test_rejects_public_forbidden_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata = valid_model_metadata()
            metadata["data_generation"]["private_cache_path"] = "/Users/me/.cache/qwen"
            write_artifact(tmp, metadata=metadata)

            with self.assertRaisesRegex(ManifestError, "forbidden public metadata key"):
                build_manifest(Path(tmp))

    def test_rejects_missing_model_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp) / "jarvis" / "2026-06-02"
            artifact_dir.mkdir(parents=True)
            (artifact_dir / "jarvis.json").write_text(
                json.dumps(valid_model_metadata(), ensure_ascii=False),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ManifestError, "missing model file"):
                build_manifest(Path(tmp))

    def test_rejects_artifact_like_directory_with_invalid_generation_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp) / "jarvis" / "2026-6-2"
            artifact_dir.mkdir(parents=True)
            (artifact_dir / "jarvis.json").write_text(
                json.dumps(valid_model_metadata(), ensure_ascii=False),
                encoding="utf-8",
            )
            (artifact_dir / "jarvis.tflite").write_bytes(b"model")

            with self.assertRaisesRegex(ManifestError, "generation_start_date"):
                build_manifest(Path(tmp))

    def test_rejects_invalid_generation_date_when_directory_contains_any_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp) / "jarvis" / "2026-6-2"
            artifact_dir.mkdir(parents=True)
            (artifact_dir / "other.json").write_text(
                json.dumps({"schema_version": 1}), encoding="utf-8"
            )

            with self.assertRaisesRegex(ManifestError, "generation_start_date"):
                build_manifest(Path(tmp))

    def test_check_manifest_requires_canonical_rendering(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "wake_word_manifest.json"
            manifest_path.write_text(
                '{"schema_version":1,"model_count":0,"models":[]}',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ManifestError, "out of date"):
                check_manifest(Path(tmp))


if __name__ == "__main__":
    unittest.main()

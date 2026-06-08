import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "scripts" / "manifest" / "generate.py"


def valid_model_metadata(
    slug="jarvis",
    display="자비스",
    date="2026-06-02",
    version=None,
):
    artifact_segment = version or date
    metadata = {
        "schema_version": 1,
        "wakeword": {
            "display": display,
            "slug": slug,
            "language": "ko",
        },
        "artifact": {
            "generation_start_date": date,
            "model_path": f"{slug}/{artifact_segment}/{slug}.tflite",
            "json_path": f"{slug}/{artifact_segment}/{slug}.json",
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
    if version is not None:
        metadata["artifact"]["generation_version"] = version
        metadata["artifact"]["generation_started_at"] = (
            f"{version[:10]}T{version[11:13]}:{version[14:16]}:{version[17:19]}Z"
        )
    return metadata


def write_artifact(
    root,
    slug="jarvis",
    display="자비스",
    date="2026-06-02",
    version=None,
):
    artifact_segment = version or date
    artifact_dir = Path(root) / slug / artifact_segment
    artifact_dir.mkdir(parents=True)
    (artifact_dir / f"{slug}.json").write_text(
        json.dumps(
            valid_model_metadata(
                slug=slug,
                display=display,
                date=date,
                version=version,
            ),
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (artifact_dir / f"{slug}.tflite").write_bytes(b"model")


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class ManifestCliTests(unittest.TestCase):
    def test_write_then_check_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_artifact(tmp)

            write_result = run_cli("--repo-root", tmp, "--write")
            self.assertEqual(write_result.returncode, 0, write_result.stderr)

            check_result = run_cli("--repo-root", tmp, "--check")
            self.assertEqual(check_result.returncode, 0, check_result.stderr)
            self.assertIn("wake_word_manifest.json is valid", check_result.stdout)

            manifest = json.loads(
                (Path(tmp) / "wake_word_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["model_count"], 1)

    def test_timestamped_artifact_write_then_check_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_artifact(tmp, version="2026-06-02T08-33-12Z")

            write_result = run_cli("--repo-root", tmp, "--write")
            self.assertEqual(write_result.returncode, 0, write_result.stderr)

            check_result = run_cli("--repo-root", tmp, "--check")
            self.assertEqual(check_result.returncode, 0, check_result.stderr)

            manifest = json.loads(
                (Path(tmp) / "wake_word_manifest.json").read_text(encoding="utf-8")
            )
            artifact = manifest["models"][0]["artifact"]
            self.assertEqual(artifact["generation_version"], "2026-06-02T08-33-12Z")

    def test_check_rejects_noncanonical_manifest_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "wake_word_manifest.json").write_text(
                '{"schema_version":1,"model_count":0,"models":[]}',
                encoding="utf-8",
            )

            result = run_cli("--repo-root", tmp, "--check")

            self.assertEqual(result.returncode, 1)
            self.assertIn("out of date", result.stderr)

    def test_invalid_artifact_folder_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp) / "jarvis" / "2026-6-2"
            artifact_dir.mkdir(parents=True)
            (artifact_dir / "other.json").write_text(
                json.dumps({"schema_version": 1}), encoding="utf-8"
            )

            result = run_cli("--repo-root", tmp)

            self.assertEqual(result.returncode, 1)
            self.assertIn("generation_version", result.stderr)


if __name__ == "__main__":
    unittest.main()

import gzip
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parent.parent / "tools" / "build.py"
TYPE = {"id": "sample-course", "label": "Sample course", "guides": ["sample-format.md"]}


def write_pack(base: Path, **changes) -> Path:
    folder = base / "sample-course"
    (folder / "project-types").mkdir(parents=True)
    (folder / "guides").mkdir()
    manifest = {"format": "dashboard-pipeline-pack", "version": "0.1", "id": "sample-course", "pack_version": "0.1.0",
                "label": "Sample course", "summary": "A test pack.", "app_min": "0.6.87",
                "project_types": ["sample-course"], "guides": ["sample-format.md"], "checks": [], "connectors": [], **changes}
    (folder / "pack.json").write_text(json.dumps(manifest), "utf-8")
    (folder / "project-types" / "sample-course.json").write_text(json.dumps(TYPE), "utf-8")
    (folder / "guides" / "sample-format.md").write_text("# Format\n", "utf-8")
    return folder


def build(packs: Path, out: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", str(BUILD), "--packs", str(packs), "--out", str(out)], capture_output=True, text=True)


class BuildTest(unittest.TestCase):
    def test_builds_a_reproducible_archive_and_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            write_pack(base / "packs")
            first = build(base / "packs", base / "a")
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(build(base / "packs", base / "b").returncode, 0)
            for name in ("sample-course-0.1.0.tar.gz", "pipeline-packs.json", "SHA256SUMS"):
                self.assertEqual((base / "a" / name).read_bytes(), (base / "b" / name).read_bytes(), name)
            index = json.loads((base / "a" / "pipeline-packs.json").read_text("utf-8"))
            self.assertEqual((index["format"], index["version"]), ("dashboard-pipeline-pack-index", "0.1"))
            entry = index["packs"][0]
            self.assertEqual(entry["archive"], "sample-course-0.1.0.tar.gz")
            self.assertEqual(entry["summary"], "A test pack.")
            with tarfile.open(fileobj=io.BytesIO(gzip.decompress((base / "a" / entry["archive"]).read_bytes()))) as tar:
                self.assertEqual(sorted(tar.getnames()), ["sample-course/guides/sample-format.md", "sample-course/pack.json",
                                                          "sample-course/project-types/sample-course.json"])

    def test_refuses_unlisted_files_and_a_mismatched_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            folder = write_pack(base / "packs", id="other-id")
            (folder / "guides" / "extra.md").write_text("x", "utf-8")
            (folder / "run.sh").write_text("echo hi", "utf-8")
            result = build(base / "packs", base / "out")
            self.assertEqual(result.returncode, 1)
            self.assertIn("id must be the folder name", result.stderr)
            self.assertIn("guides/extra.md is not listed", result.stderr)
            self.assertIn("run.sh is not pack.json", result.stderr)
            self.assertFalse((base / "out").exists())

    def test_no_packs_is_not_a_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "packs").mkdir()
            result = build(Path(tmp) / "packs", Path(tmp) / "out")
            self.assertEqual(result.returncode, 0)
            self.assertIn("nothing to release", result.stdout)


if __name__ == "__main__":
    unittest.main()

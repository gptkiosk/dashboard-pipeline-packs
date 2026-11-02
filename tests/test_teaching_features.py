"""All teaching packs carry the same bounded cross-feature contract."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TeachingFeatures(unittest.TestCase):
    def test_all_teaching_templates_share_the_guide_and_honest_visual_boundary(self):
        texts = []
        for name in ("upubhub-class", "upubhub-textbook", "upubhub-lesson-plan"):
            folder = ROOT / "packs" / name
            manifest = json.loads((folder / "pack.json").read_text())
            project = json.loads((folder / "project-types" / (name + ".json")).read_text())
            self.assertIn("textbook-learning-features.md", manifest["guides"])
            self.assertIn("textbook-learning-features.md", project["guides"])
            self.assertIn("Cross-feature review", project["planner_text"])
            self.assertIn("current push format is unchanged", project["planner_text"])
            guide = (folder / "guides" / "textbook-learning-features.md").read_text()
            for required in ("AI grades remain provisional", "Do not claim they are already deployed", "fabricate statistical data", "teacher"):
                self.assertIn(required, guide)
            texts.append(guide)
        self.assertEqual(len(set(texts)), 1)

    def test_geology_has_a_subject_code_without_changing_existing_choices(self):
        project = json.loads((ROOT / "packs/upubhub-class/project-types/upubhub-class.json").read_text())
        choices = next(s["options"] for s in project["customize"] if s["id"] == "subject_code")
        self.assertIn("GEOL", choices)
        self.assertIn("SCI", choices)
        self.assertIn("GEOG", choices)

"""Quality regression tests for P Discovery output (stdlib only).

Run: python3 -m unittest discover -s .agents/skills/p-discovery/tests -v
"""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "p_discovery_validate", ROOT / "scripts" / "validate.py"
)
assert spec is not None and spec.loader is not None
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

SAMPLE = json.loads(
    (ROOT / "examples" / "ggplot2-mini.json").read_text(encoding="utf-8")
)


class DiscoveryQualityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = copy.deepcopy(SAMPLE)

    def messages(self) -> str:
        return "\n".join(validator.validate(self.doc))

    def test_sample_passes(self) -> None:
        self.assertEqual([], validator.validate(self.doc))

    def test_claim_without_evidence_fails(self) -> None:
        self.doc["possibilities"][0]["evidence_refs"] = []
        self.assertIn("needs claim-specific", self.messages())

    def test_quote_cannot_be_fabricated(self) -> None:
        self.doc["possibilities"][0]["evidence_refs"][0]["quote"] = (
            "This sentence was invented."
        )
        self.assertIn("quote not present", self.messages())

    def test_quote_must_point_to_correct_source(self) -> None:
        self.doc["possibilities"][0]["evidence_refs"][0]["source_id"] = "src-patchwork"
        self.assertIn("quote not present", self.messages())
        self.assertIn("must also appear in source_ids", self.messages())

    def test_source_url_must_be_real_http_url_shape(self) -> None:
        self.doc["sources"][0]["url"] = "https://"
        self.assertIn("invalid http(s) URL", self.messages())

    def test_missing_source_passage_fails(self) -> None:
        self.doc["sources"][0]["evidence"] = ""
        self.assertIn("missing captured evidence", self.messages())

    def test_reviewed_requires_human_reviewer(self) -> None:
        self.doc["possibilities"][0]["status"] = "reviewed"
        self.assertIn("needs human reviewed_by", self.messages())

    def test_reviewed_with_human_record_can_pass_structural_gate(self) -> None:
        self.doc["possibilities"][0]["status"] = "reviewed"
        self.doc["possibilities"][0]["reviewed_by"] = "human-review-2026-11"
        self.assertEqual([], validator.validate(self.doc))

    def test_proposal_can_exist_without_evidence_but_is_not_confirmed(self) -> None:
        self.doc["possibilities"][0]["status"] = "proposed"
        self.doc["possibilities"][0]["source_ids"] = []
        self.doc["possibilities"][0]["evidence_refs"] = []
        self.assertEqual([], validator.validate(self.doc))

    def test_extension_without_conditions_fails(self) -> None:
        self.doc["possibilities"][1]["conditions"] = ""
        self.assertIn("extension must name conditions", self.messages())

    def test_unknown_group_fails(self) -> None:
        self.doc["possibilities"][0]["group_ids"] = ["missing-group"]
        self.assertIn("unknown group_ids", self.messages())

    def test_unknown_source_fails(self) -> None:
        self.doc["possibilities"][0]["source_ids"] = ["missing-source"]
        self.assertIn("unknown source_ids", self.messages())

    def test_duplicate_id_across_types_fails(self) -> None:
        self.doc["groups"][0]["id"] = self.doc["sources"][0]["id"]
        self.assertIn("Duplicate ID", self.messages())

    def test_root_must_be_json_object(self) -> None:
        self.assertEqual(
            ["Root must be a JSON object"], validator.validate(["wrong"])
        )


if __name__ == "__main__":
    unittest.main()

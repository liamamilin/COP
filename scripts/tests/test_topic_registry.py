"""Regression tests for Topic Registry eligibility, lifecycle, and queue derivation."""
from __future__ import annotations
import importlib.util
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / "validate_topic_registry.py"
spec = importlib.util.spec_from_file_location("topic_registry_validator", FILE)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

def fixture():
    tax = {
        "schema_version": "0.4",
        "domains": [{"id": "d", "title": "Domain"}],
        "areas": [
            {"id": "a", "domain_id": "d", "coverage_state": "taxonomy_seeded_not_exhaustive"},
            {"id": "empty", "domain_id": "d", "coverage_state": "unseeded_needs_discovery"}
        ]
    }
    reg = {
        "schema_version": "0.4",
        "items": [
            {"slug": "ready-topic", "title": "Ready Topic", "description": "A bounded subject",
             "area_id": "a", "domain_id": "d", "scope_level": "bounded_subject",
             "research_state": "candidate", "selection_status": "eligible",
             "identity_status": "source_checked", "official_url": "https://example.org",
             "related_topics": ["unverified-topic"]},
            {"slug": "unverified-topic", "title": "Unverified Topic", "description": "A candidate",
             "area_id": "a", "domain_id": "d", "scope_level": "bounded_subject",
             "research_state": "candidate", "selection_status": "candidate",
             "identity_status": "unverified", "official_url": None,
             "related_topics": ["ready-topic"]}
        ]
    }
    waves = {"schema_version": "0.4", "max_parallel_global": 2,
             "waves": [{"id": "w1", "state": "proposed_not_started",
                        "max_parallel": 2,
                        "topic_slugs": ["ready-topic", "unverified-topic"]}]}
    return tax, reg, waves

class TopicRegistryTests(unittest.TestCase):
    def test_seeded_and_unseeded_are_both_valid(self):
        tax, reg, _ = fixture()
        topics = module.validate(tax, reg)
        self.assertEqual(set(topics), {"ready-topic", "unverified-topic"})

    def test_no_fake_empty_area(self):
        tax, reg, _ = fixture()
        tax["areas"][1]["coverage_state"] = "taxonomy_seeded_not_exhaustive"
        with self.assertRaisesRegex(ValueError, "Unseeded area"):
            module.validate(tax, reg)

    def test_eligible_requires_checked_identity_and_https_source(self):
        tax, reg, _ = fixture()
        reg["items"][0]["official_url"] = ""
        with self.assertRaisesRegex(ValueError, "No official source"):
            module.validate(tax, reg)
        reg["items"][0]["official_url"] = "https://example.org"
        reg["items"][0]["identity_status"] = "unverified"
        with self.assertRaisesRegex(ValueError, "Unverified identity"):
            module.validate(tax, reg)

    def test_unverified_deferred_and_only_ready_queued(self):
        tax, reg, waves = fixture()
        topics = module.validate(tax, reg)
        q = module.build_queue(reg, topics, waves)
        self.assertEqual([x["slug"] for x in q["executable"]], ["ready-topic"])
        self.assertEqual([x["slug"] for x in q["deferred_preferred"]], ["unverified-topic"])

    def test_queue_rebuild_idempotent(self):
        tax, reg, waves = fixture()
        topics = module.validate(tax, reg)
        q1 = module.build_queue(reg, topics, waves)
        q2 = module.build_queue(reg, topics, q1)
        self.assertEqual(q1, q2)

    def test_completed_topic_not_requeued(self):
        tax, reg, waves = fixture()
        reg["items"][0]["research_state"] = "review"
        reg["items"][0]["selection_status"] = "review"
        topics = module.validate(tax, reg)
        q = module.build_queue(reg, topics, waves)
        self.assertEqual(q["executable"], [])

    def test_eligible_state_allowed(self):
        tax, reg, waves = fixture()
        reg["items"][0]["research_state"] = "eligible"
        topics = module.validate(tax, reg)
        self.assertEqual(len(module.build_queue(reg, topics, waves)["executable"]), 1)

    def test_blocked_topic_not_queued(self):
        tax, reg, waves = fixture()
        t = reg["items"][0]
        t["research_state"] = "blocked"
        t["selection_status"] = "blocked"
        topics = module.validate(tax, reg)
        q = module.build_queue(reg, topics, waves)
        self.assertEqual(q["executable"], [])

    def test_invalid_relation_rejected(self):
        tax, reg, _ = fixture()
        reg["items"][1]["related_topics"] = ["missing-topic"]
        with self.assertRaisesRegex(ValueError, "Bad relation"):
            module.validate(tax, reg)

    def test_lifecycle_rules_are_not_fixed_to_seed_counts(self):
        self.assertIn("researching", module.TRANSITIONS["eligible"])
        self.assertIn("rework", module.TRANSITIONS["review"])
        self.assertNotIn("published", module.TRANSITIONS["candidate"])
        tax, reg, _ = fixture()
        reg["items"].append(
            {"slug": "new-item", "title": "New Item", "description": "Another candidate",
             "area_id": "a", "domain_id": "d", "scope_level": "bounded_subject",
             "research_state": "candidate", "selection_status": "candidate",
             "identity_status": "unverified", "related_topics": []})
        self.assertEqual(len(module.validate(tax, reg)), 3)

    def test_state_change_persists_and_rebuilds_queue(self):
        tax, reg, waves = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "catalog").mkdir()
            data = {"topic-taxonomy.v0.4.json": tax,
                    "topic-registry.v0.4.json": reg,
                    "research-queue.v0.4.json": waves}
            for filename, value in data.items():
                (base / "catalog" / filename).write_text(
                    json.dumps(value), encoding="utf-8")
            with patch.object(module, "ROOT", base), patch.object(
                sys, "argv", ["validate_topic_registry.py", "--set-status",
                              "ready-topic", "eligible"]):
                module.main()
            saved = json.loads((base / "catalog/topic-registry.v0.4.json").read_text())
            q = json.loads((base / "catalog/research-queue.v0.4.json").read_text())
            self.assertEqual(saved["items"][0]["research_state"], "eligible")
            self.assertEqual(saved["items"][0]["state_history"][-1]["from"], "candidate")
            self.assertEqual([x["slug"] for x in q["executable"]], ["ready-topic"])
            self.assertEqual(
                module.build_queue(saved, {x["slug"]: x for x in saved["items"]}, q), q)

    def test_blocking_requires_reason_and_removes_from_queue(self):
        tax, reg, waves = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "catalog").mkdir()
            for filename, value in {
                "topic-taxonomy.v0.4.json": tax,
                "topic-registry.v0.4.json": reg,
                "research-queue.v0.4.json": waves
            }.items():
                (base / "catalog" / filename).write_text(
                    json.dumps(value), encoding="utf-8")
            with patch.object(module, "ROOT", base), patch.object(
                sys, "argv", ["validate_topic_registry.py", "--set-status",
                              "ready-topic", "blocked"]):
                with self.assertRaisesRegex(ValueError, "Missing review/change reason"):
                    module.main()
            with patch.object(module, "ROOT", base), patch.object(
                sys, "argv", ["validate_topic_registry.py", "--set-status",
                              "ready-topic", "blocked", "--reason", "identity disputed"]):
                module.main()
            q = json.loads((base / "catalog/research-queue.v0.4.json").read_text())
            self.assertEqual(q["executable"], [])
            self.assertEqual(q["deferred_preferred"][0]["reason"], "blocked")

if __name__ == "__main__":
    unittest.main()

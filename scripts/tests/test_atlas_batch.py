"""Regression checks for errors found in the first Luna research handoff."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("atlas_batch", REPO / "scripts/verify_atlas_batch.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class BatchHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="atlas-batch-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "catalog").mkdir()
        for name in ["p-atlas-topics.v0.1.json", "p-atlas-topics.v0.2.json"]:
            shutil.copy2(REPO / "catalog" / name, self.root / "catalog" / name)
        self.directory = self.root / "outputs/nextjs"
        shutil.copytree(REPO / "outputs/nextjs", self.directory)
        validator = self.root / ".agents/skills/p-discovery/scripts/validate.py"
        validator.parent.mkdir(parents=True)
        validator.symlink_to(REPO / ".agents/skills/p-discovery/scripts/validate.py")
        self.data_path = self.directory / "possibilities.json"
        self.data = json.loads(self.data_path.read_text())

    def run_audit(self, *extra):
        argv = ["verify_atlas_batch.py", "--catalog",
                str(self.root / "catalog/p-atlas-topics.v0.2.json"), "--topics", "nextjs", *extra]
        with patch.object(AUDIT, "ROOT", self.root), patch("sys.argv", argv), contextlib.redirect_stdout(io.StringIO()):
            AUDIT.main()

    def save_data(self):
        self.data_path.write_text(json.dumps(self.data, ensure_ascii=False))

    def test_real_saved_handoff_passes_without_private_cache(self):
        self.run_audit("--require-all")

    def test_fabricated_quote_is_rejected(self):
        self.data["possibilities"][0]["evidence_refs"][0]["quote"] = "Fabricated capability that was never captured"
        self.save_data()
        with self.assertRaisesRegex(ValueError, "quote not present"):
            self.run_audit()

    def test_copy_pasted_display_line_cannot_contradict_numeric_locator(self):
        self.data["possibilities"][0]["evidence_refs"][0]["location"] = "页面正文；HTML 提取正文行 999999–999999"
        self.save_data()
        with self.assertRaisesRegex(ValueError, "display location contradicts"):
            self.run_audit()

    def test_capture_hash_must_agree_with_the_coverage_record(self):
        self.data["sources"][0]["capture_sha256"] = "0" * 64
        self.save_data()
        with self.assertRaisesRegex(ValueError, "inconsistent capture hash"):
            self.run_audit()

    def test_markdown_response_is_not_described_as_html_extraction(self):
        coverage = json.loads((self.directory / "source-coverage.json").read_text())
        markdown_ids = {c["id"] for c in coverage["retrieved"] if "markdown" in c.get("content_type", "")}
        ref = next(r for p in self.data["possibilities"] for r in p["evidence_refs"]
                   if r["source_id"] in markdown_ids)
        ref["line_basis"] = "extracted_html_text"
        self.save_data()
        with self.assertRaisesRegex(ValueError, "Markdown response mislabeled"):
            self.run_audit()

    def test_moving_github_file_cannot_masquerade_as_fixed_evidence(self):
        source = next(s for s in self.data["sources"] if "github.com/" in s["url"] and "/blob/" in s["url"])
        pieces = source["url"].split("/")
        pieces[6] = "canary"
        source["url"] = "/".join(pieces)
        self.save_data()
        with self.assertRaisesRegex(ValueError, "not fixed to a commit"):
            self.run_audit()

    def test_complete_files_do_not_promote_a_planned_topic(self):
        path = self.root / "catalog/p-atlas-topics.v0.2.json"
        catalog = json.loads(path.read_text())
        topic = next(t for t in catalog["topics"] if t["slug"] == "nextjs")
        topic["status"] = "planned"
        topic["research_status"] = "revision_needed"
        path.write_text(json.dumps(catalog))
        with self.assertRaisesRegex(ValueError, "awaiting evidence handoff"):
            self.run_audit("--require-all")

    def test_report_cannot_omit_updated_conditions(self):
        self.data["possibilities"][0]["conditions"] += " 必须先核对当前访问权限。"
        self.save_data()
        with self.assertRaisesRegex(ValueError, "report conditions differs"):
            self.run_audit()

    def test_report_cannot_keep_a_stale_result(self):
        self.data["possibilities"][0]["result"] += " 此结果须按项目配置交付。"
        self.save_data()
        with self.assertRaisesRegex(ValueError, "report result differs"):
            self.run_audit()

    def test_report_cannot_mislabel_extension_as_core(self):
        path = self.directory / "possibilities.md"
        path.write_text(path.read_text().replace("（扩展）", "（核心）", 1))
        with self.assertRaisesRegex(ValueError, "capability label differs"):
            self.run_audit()

    def test_report_cannot_link_to_an_unpinned_github_branch(self):
        ref = next(r for p in self.data["possibilities"] for r in p["evidence_refs"]
                   if "github.com/" in r["url"] and "/blob/" in r["url"])
        pieces = ref["url"].split("/")
        pieces[6] = "canary"
        path = self.directory / "possibilities.md"
        path.write_text(path.read_text().replace(ref["url"], "/".join(pieces)))
        with self.assertRaisesRegex(ValueError, "report lacks the corresponding evidence link"):
            self.run_audit()

    def test_new_catalog_cannot_change_an_existing_domain(self):
        path = self.root / "catalog/p-atlas-topics.v0.2.json"
        catalog = json.loads(path.read_text())
        catalog["domains"][0]["title"] = "Changed published navigation"
        path.write_text(json.dumps(catalog))
        with self.assertRaisesRegex(ValueError, "Changed published domain"):
            self.run_audit()

    def test_proposed_direction_can_remain_unconfirmed(self):
        p = dict(self.data["possibilities"][0], id="p-proposed-test", title="待验证的研究方向",
                 status="proposed", source_ids=[], evidence_refs=[])
        self.data["possibilities"].append(p)
        self.save_data()
        markdown = self.directory / "possibilities.md"
        markdown.write_text(markdown.read_text() +
                            f"\n## 待验证\n\n### {p['title']}\n\n{p['result']}\n\n"
                            f"**扩展**\n\n{p['conditions']}\n")
        self.run_audit()


if __name__ == "__main__":
    unittest.main()

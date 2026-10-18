"""Offline tests for evidence chain verification (T04).

Verifies: tool_call_id linkage, re-execution match, content hash,
multi-call support, and negative cases (mismatch, missing linkage, unknown tool).
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from evidence import (
    compute_evidence_hash,
    extract_tool_call_chain,
    re_execute_tool,
    verify_multi_call_evidence,
    verify_single_call_evidence,
)


def _offline_run_data() -> dict:
    from agent import build_offline_agent, invoke_agent, inspect_response

    agent = build_offline_agent()
    result = invoke_agent(agent, "P001 的价格是多少？")
    return {
        "mode": "offline-mock",
        **inspect_response(result, "P001 的价格是多少？"),
    }


class TestReExecuteTool:
    def test_valid_product(self):
        result = re_execute_tool("get_product_info", {"product_id": "P001"})
        assert result["name"] == "LangChain 入门教程"
        assert result["price"] == 99.0

    def test_unknown_product(self):
        result = re_execute_tool("get_product_info", {"product_id": "P999"})
        assert "error" in result

    def test_unknown_tool_raises(self):
        with pytest.raises(ValueError, match="Unknown tool"):
            re_execute_tool("nonexistent_tool", {"x": 1})

    def test_all_five_products(self):
        for pid in ("P001", "P002", "P003", "P004", "P005"):
            result = re_execute_tool("get_product_info", {"product_id": pid})
            assert "error" not in result
            assert "name" in result


class TestExtractToolCallChain:
    def test_extracts_single_pair(self):
        run = _offline_run_data()
        pairs = extract_tool_call_chain(run["messages"])
        assert len(pairs) == 1
        assert pairs[0]["tool_call"]["name"] == "get_product_info"

    def test_rejects_unmatched_tool_call(self):
        messages = [
            {"type": "human", "content": "hello"},
            {"type": "ai", "content": "", "tool_calls": [
                {"name": "get_product_info", "args": {"product_id": "P001"}, "id": "call_orphan"},
            ]},
        ]
        with pytest.raises(ValueError, match="no matching Tool message"):
            extract_tool_call_chain(messages)

    def test_rejects_no_tool_calls(self):
        messages = [
            {"type": "human", "content": "hello"},
            {"type": "ai", "content": "just text"},
        ]
        with pytest.raises(ValueError, match="No tool_call"):
            extract_tool_call_chain(messages)


class TestVerifySingleCallEvidence:
    def test_offline_run_verifies(self):
        run = _offline_run_data()
        report = verify_single_call_evidence(run)
        assert report["verified"] is True
        assert report["re_execution_match"] is True
        assert report["tool_name"] == "get_product_info"
        assert report["tool_args"]["product_id"] == "P001"

    def test_rejects_tampered_tool_result(self):
        run = _offline_run_data()
        for msg in run["messages"]:
            if msg["type"] == "tool":
                msg["content"] = json.dumps({"name": "TAMPERED", "price": 0.0})
        report = verify_single_call_evidence(run)
        assert report["verified"] is False
        assert "mismatch" in report["reason"]

    def test_rejects_too_few_messages(self):
        run = {"messages": [{"type": "human", "content": "hi"}, {"type": "ai", "content": "ok"}]}
        report = verify_single_call_evidence(run)
        assert report["verified"] is False

    def test_rejects_empty_final_answer(self):
        run = _offline_run_data()
        run["messages"][-1]["content"] = ""
        report = verify_single_call_evidence(run)
        assert report["verified"] is False

    def test_rejects_multiple_pairs(self):
        run = _offline_run_data()
        run["messages"].append({
            "type": "ai",
            "content": "",
            "tool_calls": [{"name": "get_product_info", "args": {"product_id": "P002"}, "id": "call_002"}],
        })
        run["messages"].append({
            "type": "tool",
            "content": json.dumps({"name": "Agent"}),
            "tool_call_id": "call_002",
        })
        run["messages"].append({"type": "ai", "content": "combined answer"})
        report = verify_single_call_evidence(run)
        assert report["verified"] is False
        assert "Expected 1" in report["reason"]


class TestVerifyMultiCallEvidence:
    def test_single_call_passes_multi_verify(self):
        run = _offline_run_data()
        report = verify_multi_call_evidence(run)
        assert report["verified"] is True
        assert report["pair_count"] == 1

    def test_rejects_tampered_result_in_multi(self):
        run = _offline_run_data()
        for msg in run["messages"]:
            if msg["type"] == "tool":
                msg["content"] = json.dumps({"name": "WRONG"})
        report = verify_multi_call_evidence(run)
        assert report["verified"] is False
        assert report["pairs"][0]["verified"] is False


class TestComputeEvidenceHash:
    def test_hash_is_deterministic(self):
        run = _offline_run_data()
        h1 = compute_evidence_hash(run)
        h2 = compute_evidence_hash(run)
        assert h1 == h2
        assert len(h1) == 64

    def test_hash_changes_when_result_tampered(self):
        run = _offline_run_data()
        h_original = compute_evidence_hash(run)
        run["tool_result"] = {"name": "TAMPERED"}
        h_tampered = compute_evidence_hash(run)
        assert h_original != h_tampered

    def test_hash_changes_when_answer_tampered(self):
        run = _offline_run_data()
        h_original = compute_evidence_hash(run)
        run["answer"] = "completely different answer"
        h_tampered = compute_evidence_hash(run)
        assert h_original != h_tampered

    def test_hash_ignores_metadata_fields(self):
        run = _offline_run_data()
        h1 = compute_evidence_hash(run)
        run["mode"] = "changed"
        run["note"] = "changed"
        run["configuration"] = {"changed": True}
        h2 = compute_evidence_hash(run)
        assert h1 == h2


class TestT06NegativeIntegration:
    """T06: explicit negative examples from T01 §3.3.

    These tests verify that the evidence chain verifier rejects each specific
    failure mode that T06 requires: tool not called, wrong args, result not used,
    error ignored, and evidence tampering.
    """

    def test_tool_not_called_model_fabricates(self):
        """Model claims product info without calling tool (no tool_calls)."""
        messages = [
            {"type": "human", "content": "P001 的价格是多少？"},
            {"type": "ai", "content": "P001 的价格是 99.00 元。"},
        ]
        run = {"messages": messages}
        report = verify_single_call_evidence(run)
        assert report["verified"] is False
        assert "too short" in report["reason"].lower() or "No tool_call" in str(report)

    def test_tool_called_with_wrong_args(self):
        """Model calls tool with args that don't match user question."""
        run = _offline_run_data()
        for msg in run["messages"]:
            if msg.get("tool_calls"):
                msg["tool_calls"][0]["args"] = {"product_id": "P999"}
        run["tool_args"] = {"product_id": "P999"}
        report = verify_single_call_evidence(run)
        assert report["verified"] is False
        assert "mismatch" in report["reason"]

    def test_tool_returns_error_but_model_claims_exists(self):
        """Tool returns error, but recorded result claims product exists."""
        run = _offline_run_data()
        for msg in run["messages"]:
            if msg["type"] == "tool":
                msg["content"] = json.dumps({"error": "Product not found", "product_id": "P001"})
        run["tool_result"] = {"error": "Product not found", "product_id": "P001"}
        report = verify_single_call_evidence(run)
        assert report["verified"] is False
        assert "mismatch" in report["reason"]

    def test_answer_tampered_but_tool_result_correct(self):
        """Tool result is correct, but final answer is changed."""
        run = _offline_run_data()
        original_hash = compute_evidence_hash(run)
        run["answer"] = "P001 的价格是 0.00 元。"
        run["messages"][-1]["content"] = "P001 的价格是 0.00 元。"
        new_hash = compute_evidence_hash(run)
        assert original_hash != new_hash
        report = verify_single_call_evidence(run)
        assert report["verified"] is True
        assert compute_evidence_hash(run) != original_hash

    def test_multi_call_one_tampered_one_valid(self):
        """Two tool calls: first valid, second tampered."""
        run = _offline_run_data()
        run["messages"].append({
            "type": "ai",
            "content": "",
            "tool_calls": [{"name": "get_product_info", "args": {"product_id": "P002"}, "id": "call_002"}],
        })
        run["messages"].append({
            "type": "tool",
            "content": json.dumps({"name": "TAMPERED", "price": 0.0}),
            "tool_call_id": "call_002",
        })
        run["messages"].append({"type": "ai", "content": "combined answer"})
        report = verify_multi_call_evidence(run)
        assert report["verified"] is False
        assert report["pair_count"] == 2
        assert report["pairs"][0]["verified"] is True
        assert report["pairs"][1]["verified"] is False

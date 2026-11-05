#!/usr/bin/env python3
"""Audit the 17-topic research batch without changing P Discovery's contract.

Default: reproducible metadata/locator/report checks, without network or caches.
--verify-pinned: re-fetch immutable GitHub Markdown files and check bytes/lines.
--cache-dir: additionally compare every excerpt with the original local capture.
Neither mode certifies semantic entailment, completeness, or product execution.
"""

import argparse
import collections
import concurrent.futures
import hashlib
import html
import json
from pathlib import Path
import re
import urllib.request
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
TOPICS = (
    "agent-harness", "langgraph", "mcp", "llm-inference", "llm-finetuning",
    "ollama", "codex", "claude-code", "opencode", "playwright",
    "ai-video-generation", "ai-music-production", "ai-voice", "r-data-analysis",
    "paperless-ngx", "changedetection", "research-workflows",
)
PIN = re.compile(r"https://raw\.githubusercontent\.com/([^/]+/[^/]+)/([0-9a-f]{40})/(.+)")
MOVING = re.compile(r"https://raw\.githubusercontent\.com/[^/]+/[^/]+/(main|master)/")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def norm(text):
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def public_url(url):
    parts = urlsplit(url)
    return parts.scheme == "https" and bool(parts.hostname) and not parts.username


def check_text(text, refs, label):
    lines = html.unescape(text).splitlines()
    for ref in refs:
        lo, hi = ref["source_line_start"], ref["source_line_end"]
        require(hi <= len(lines), f"{label}: line outside captured text")
        require(norm(ref["quote"]) in norm("\n".join(lines[lo - 1:hi])),
                f"{label}: quote not within stated lines")


def fetch_pin(item):
    url, (digest, refs) = item
    # Only exact-commit public raw GitHub files are eligible for network access.
    require(PIN.fullmatch(url) is not None, f"Invalid pinned URL: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "COP-research-audit/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        require(response.url == url, f"Unexpected redirect: {url}")
        body = response.read()
    require(hashlib.sha256(body).hexdigest() == digest, f"Hash mismatch: {url}")
    check_text(body.decode("utf-8"), refs, url)
    return url


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-pinned", action="store_true")
    parser.add_argument("--cache-dir", type=Path)
    args = parser.parse_args()
    words = collections.Counter()
    pins = {}
    totals = collections.Counter()
    source_urls = set()
    for slug in TOPICS:
        directory = ROOT / "outputs" / slug
        data = read(directory / "possibilities.json")
        markdown = (directory / "possibilities.md").read_text(encoding="utf-8")
        coverage = read(directory / "source-coverage.json")
        captures = {c["id"]: c for c in coverage["retrieved"]}
        sources = {s["id"]: s for s in data["sources"]}
        require(data["research"].get("evidence_audit_version") == "1", f"{slug}: missing audit version")
        require(len(sources) == len(data["sources"]), f"{slug}: duplicate source ID")
        require(len({p["id"] for p in data["possibilities"]}) == len(data["possibilities"]),
                f"{slug}: duplicate possibility ID")
        used = collections.defaultdict(list)
        for p in data["possibilities"]:
            label = f"{slug}/{p['id']}"
            require(p["status"] == "source_supported", f"{label}: unexpected review claim")
            require(f"### `{p['id']}` {p['title']}" in markdown and p["result"] in markdown,
                    f"{label}: report differs from JSON")
            refs = p.get("evidence_refs", [])
            require(bool(refs) and set(p["source_ids"]) == {r["source_id"] for r in refs},
                    f"{label}: evidence/source mismatch")
            for ref in refs:
                sid = ref["source_id"]
                require(sid in sources and bool(ref["quote"].strip()), f"{label}: missing evidence")
                require(ref["quote"] in sources[sid]["evidence"], f"{label}: quote absent from source record")
                require(ref.get("line_basis") in {"captured_markdown", "extracted_html_text"},
                        f"{label}: invalid line basis")
                lo, hi = ref.get("source_line_start"), ref.get("source_line_end")
                require(type(lo) is int and type(hi) is int and 0 < lo <= hi,
                        f"{label}: invalid line interval")
                require(bool(ref.get("location")) and public_url(ref.get("url", "")),
                        f"{label}: missing locator")
                require(ref["url"] in markdown, f"{label}: locator missing from report")
                if sources[sid].get("git_commit"):
                    require(ref["url"] == f"{sources[sid]['url']}#L{lo}-L{hi}", f"{label}: wrong pinned lines")
                used[sid].append(ref)
                totals["evidence_refs"] += 1
            totals["possibilities"] += 1
        require(set(used) == set(sources), f"{slug}: unused confirmed source")
        for sid, source in sources.items():
            label = f"{slug}/{sid}"
            capture = captures[sid]
            require(source["capture_sha256"] == capture["capture_sha256"], f"{label}: capture hash mismatch")
            excerpts = source["evidence"].split("\n[…]\n")
            require(set(excerpts) == {r["quote"] for r in used[sid]}, f"{label}: inconsistent excerpts")
            key = source["capture_origin"].rstrip("/")
            words[key] += sum(len(q.split()) for q in excerpts) + sum(len(r["quote"].split()) for r in used[sid])
            source_urls.add(source["url"])
            original = source.get("original_url", source["url"])
            if MOVING.match(original):
                require(bool(source.get("git_commit")), f"{label}: moving branch citation")
            if source.get("git_commit"):
                match = PIN.fullmatch(source["pinned_raw_url"])
                require(match is not None, f"{label}: invalid pinned file")
                repo, sha, path = match.groups()
                require(source["git_commit"] == sha and source["url"] == f"https://github.com/{repo}/blob/{sha}/{path}",
                        f"{label}: commit/citation mismatch")
                digest = source["pinned_content_sha256"]
                require(digest == source["capture_sha256"] and source.get("pinned_matches_capture") is True,
                        f"{label}: pin not matched to capture")
                require(capture.get("immutable_url") == source["url"] and capture.get("pinned_content_sha256") == digest,
                        f"{label}: coverage missing pin")
                pin = pins.setdefault(source["pinned_raw_url"], (digest, []))
                require(pin[0] == digest, f"{label}: conflicting hashes")
                pin[1].extend(used[sid])
                totals["pinned_records"] += 1
            if args.cache_dir:
                cached = read(args.cache_dir / slug / (sid + ".json"))
                require(cached["capture_sha256"] == source["capture_sha256"], f"{label}: original hash mismatch")
                check_text(cached["text"], used[sid], label)
                totals["cached_sources"] += 1
            totals["sources"] += 1
        totals["captures"] += len(captures)
    require(not any(n > 25 for n in words.values()), "Shared-source literal excerpt budget exceeded")
    print(f"PASS {len(TOPICS)} topics; {totals['possibilities']} P; {totals['evidence_refs']} located evidence refs")
    print(f"PASS {totals['sources']} sources / {len(source_urls)} distinct URLs; {totals['captures']} captured records")
    print(f"PASS {totals['pinned_records']} pinned source records / {len(pins)} distinct files; global excerpt budgets")
    if args.cache_dir:
        print(f"PASS original capture hashes and quote line intervals: {totals['cached_sources']} sources")
    if args.verify_pinned:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            verified = list(pool.map(fetch_pin, pins.items()))
        print(f"PASS live immutable file bytes, SHA-256 and excerpt line intervals: {len(verified)} files")
    print("Limits: metadata/text checks do not certify semantic support, completeness, or runtime behavior.")


if __name__ == "__main__":
    main()

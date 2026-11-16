#!/usr/bin/env python3
"""Check the saved Luna research batch; never promote a topic automatically.

The existing P Discovery validator remains the format authority. This command
adds capture/locator checks for the v0.2 research handoff. Without --require-all,
missing topics are reported as pending, not as successful research.
"""

import argparse
import collections
import concurrent.futures
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re
import sys
import urllib.request
from urllib.parse import urldefrag, urlsplit


ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def norm(text):
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def check_report(markdown, possibility, label):
    """Check each result in its own report entry, including its limitations."""
    title = re.escape(possibility["title"])
    entries = list(re.finditer(
        rf"(?m)^(?:- \*\*{title}\*\*[^\n]*|### {title}[ \t]*)$", markdown))
    require(len(entries) == 1, f"{label}: missing or duplicate report entry")
    entry = entries[0]
    if entry[0].startswith("-"):
        block = entry[0]
    else:
        following = re.search(r"(?m)^#{1,6} ", markdown[entry.end():])
        end = entry.end() + following.start() if following else len(markdown)
        block = markdown[entry.start():end]
    for field in ("result", "conditions"):
        value = possibility.get(field)
        if value:
            require(norm(value) in norm(block), f"{label}: report {field} differs from JSON")
    availability = {"core": "核心", "extension": "扩展", "unknown": "待确认"}[
        possibility["availability"]]
    require(f"（{availability}）" in block or f"**{availability}**" in block,
            f"{label}: report capability label differs from JSON")
    for ref in possibility.get("evidence_refs", []):
        require(f"]({ref['url']})" in block,
                f"{label}: report lacks the corresponding evidence link")


def check_line_basis(ref, content_type, label, origin=""):
    content_type = content_type.lower()
    if "markdown" in content_type:
        require(ref["line_basis"] == "captured_markdown",
                f"{label}: Markdown response mislabeled as HTML")
    elif "html" in content_type:
        require(ref["line_basis"] == "extracted_html_text",
                f"{label}: HTML response mislabeled as Markdown")
    elif origin and Path(urlsplit(origin).path).suffix.lower() in {".yml", ".yaml", ".json", ".py", ".js", ".ts"}:
        require(ref["line_basis"] == "captured_text",
                f"{label}: source code must be labeled as captured text")


def verify_pinned_file(item):
    url, (digest, refs) = item
    require(re.fullmatch(r"https://raw\.githubusercontent\.com/[^/]+/[^/]+/[0-9a-f]{40}/.+", url),
            "Only public fixed-commit GitHub files may be fetched by this option")
    request = urllib.request.Request(url, headers={"User-Agent": "COP-research-audit/0.2"})
    with urllib.request.urlopen(request, timeout=30) as response:
        require(response.url == url, f"Unexpected redirect: {url}")
        body = response.read()
    require(hashlib.sha256(body).hexdigest() == digest, f"Pinned file byte hash mismatch: {url}")
    lines = body.decode("utf-8").splitlines()
    for ref in refs:
        lo, hi = ref["source_line_start"], ref["source_line_end"]
        require(hi <= len(lines) and norm(ref["quote"]) in norm("\n".join(lines[lo - 1:hi])),
                f"Excerpt not at pinned Markdown lines: {url}")
    return url


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=ROOT / "catalog/p-atlas-topics.v0.2.json")
    parser.add_argument("--topics", nargs="+")
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--require-all", action="store_true")
    parser.add_argument("--verify-pinned", action="store_true")
    args = parser.parse_args()
    catalog = read(args.catalog)
    cohort = {t["slug"]: t for t in catalog["topics"] if t.get("edition") == "0.2"}
    require(bool(cohort), "No v0.2 research topics found")
    selected = args.topics or list(cohort)
    require(set(selected) <= set(cohort), "Unknown topic selection")
    require(len(set(selected)) == len(selected), "Duplicate topic selection")
    old = read(ROOT / "catalog/p-atlas-topics.v0.1.json")
    current = {t["slug"]: t for t in catalog["topics"]}
    for topic in old["topics"]:
        require(current.get(topic["slug"]) == topic, f"Changed published topic {topic['slug']}")
    domain_records = {d["id"]: d for d in catalog["domains"]}
    domains = set(domain_records)
    require(len(domains) == len(catalog["domains"]), "Duplicate catalog domain")
    for domain in old["domains"]:
        require(domain_records.get(domain["id"]) == domain,
                f"Changed published domain {domain['id']}")
    require(len(current) == len(catalog["topics"]), "Duplicate catalog slug")
    require(all(t["domain_id"] in domains for t in catalog["topics"]), "Unknown domain")
    if args.baseline:
        for name, digest in read(args.baseline)["files"].items():
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                    f"Protected file changed: {name}")
    spec = importlib.util.spec_from_file_location(
        "p_discovery_contract", ROOT / ".agents/skills/p-discovery/scripts/validate.py")
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    counts = collections.Counter()
    words = collections.Counter()
    pins = {}
    pending = []
    for slug in selected:
        require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug), "Invalid topic slug")
        directory = ROOT / "outputs" / slug
        names = ("possibilities.json", "possibilities.md", "validation-report.txt",
                 "discovery-log.md", "source-coverage.json")
        if not all((directory / name).is_file() for name in names):
            require(cohort[slug]["status"] != "ready", f"Ready topic lacks files: {slug}")
            pending.append(slug)
            continue
        data = read(directory / "possibilities.json")
        errors = validator.validate(data)
        require(not errors, f"{slug}: " + "; ".join(errors))
        require(data.get("research", {}).get("generation_model") == "gpt-6-luna",
                f"{slug}: missing requested author model")
        coverage = read(directory / "source-coverage.json")
        captures = {c["id"]: c for c in coverage["retrieved"]}
        require(len(captures) == len(coverage["retrieved"]), f"{slug}: duplicate capture ID")
        sources = {s["id"]: s for s in data["sources"]}
        used = collections.defaultdict(list)
        markdown = (directory / "possibilities.md").read_text(encoding="utf-8")
        for p in data["possibilities"]:
            check_report(markdown, p, f"{slug}/{p['id']}")
            if p["status"] == "proposed":
                counts["proposed"] += 1
            else:
                require(p["status"] == "source_supported", f"{slug}/{p['id']}: unexpected review claim")
                counts["supported"] += 1
            for ref in p.get("evidence_refs", []):
                label = f"{slug}/{p['id']}/{ref['source_id']}"
                require(ref.get("line_basis") in {"captured_markdown", "extracted_html_text", "captured_text"},
                        f"{label}: missing line basis")
                lo, hi = ref.get("source_line_start"), ref.get("source_line_end")
                require(type(lo) is int and type(hi) is int and 0 < lo <= hi,
                        f"{label}: invalid line interval")
                require(bool(ref.get("location")), f"{label}: missing location")
                for match in re.finditer(
                    r"第\s*(\d+)(?:\s*[–—-]\s*(\d+))?\s*行|行\s*(\d+)(?:\s*[–—-]\s*(\d+))?",
                    ref["location"],
                ):
                    start, end = (match[1], match[2]) if match[1] else (match[3], match[4])
                    require(int(start) == lo and int(end or start) == hi,
                            f"{label}: display location contradicts recorded lines")
                url = urlsplit(ref.get("url", ""))
                require(url.scheme == "https" and bool(url.hostname), f"{label}: missing HTTPS locator")
                used[ref["source_id"]].append(ref)
                counts["refs"] += 1
        require(set(used) == set(sources), f"{slug}: unused sources belong in coverage, not confirmed evidence")
        for sid, source in sources.items():
            label = f"{slug}/{sid}"
            capture = captures[sid]
            digest = source.get("capture_sha256", "")
            require(re.fullmatch(r"[0-9a-f]{64}", digest), f"{label}: invalid capture hash")
            require(digest == capture["capture_sha256"], f"{label}: inconsistent capture hash")
            require(source.get("retrieved_at") == capture["retrieved_at"], f"{label}: inconsistent capture time")
            require(source.get("capture_origin") == capture.get("capture_origin"),
                    f"{label}: inconsistent capture origin")
            require(source.get("content_type") == capture.get("content_type"),
                    f"{label}: inconsistent capture content type")
            for ref in used[sid]:
                check_line_basis(ref, capture.get("content_type", ""), label, source["capture_origin"])
            excerpts = source["evidence"].split("\n[…]\n")
            require(set(excerpts) == {ref["quote"] for ref in used[sid]}, f"{label}: inconsistent source excerpts")
            origin = urldefrag(source["capture_origin"])[0].rstrip("/")
            source_url = urlsplit(source["url"])
            if source_url.hostname == "github.com" and "/blob/" in source_url.path:
                path = source_url.path.split("/", 5)
                require(len(path) == 6 and re.fullmatch(r"[0-9a-f]{40}", path[4]),
                        f"{label}: GitHub file citation is not fixed to a commit")
                expected_raw = f"https://raw.githubusercontent.com/{path[1]}/{path[2]}/{path[4]}/{path[5]}"
                require(origin == expected_raw, f"{label}: file citation and captured revision differ")
                for ref in used[sid]:
                    ref_url, fragment = urldefrag(ref["url"])
                    line = re.fullmatch(r"L(\d+)(?:-L(\d+))?", fragment)
                    require(ref_url == urldefrag(source["url"])[0] and line is not None,
                            f"{label}: pinned citation lacks the corresponding line link")
                    require(int(line[1]) == ref["source_line_start"] and
                            int(line[2] or line[1]) == ref["source_line_end"] and
                            ref["line_basis"] in {"captured_markdown", "captured_text"},
                            f"{label}: GitHub line link differs from captured source-text lines")
            elif source_url.hostname == "raw.githubusercontent.com":
                require(re.match(r"/[^/]+/[^/]+/[0-9a-f]{40}/", source_url.path),
                        f"{label}: raw GitHub source is not fixed to a commit")
            if urlsplit(origin).hostname == "raw.githubusercontent.com":
                pin = pins.setdefault(origin, (digest, []))
                require(pin[0] == digest, f"{label}: contradictory pinned hashes")
                pin[1].extend(used[sid])
            words[origin] += sum(len(q.split()) for q in excerpts) + sum(len(r["quote"].split()) for r in used[sid])
            if args.cache_dir:
                cached = read(args.cache_dir / slug / (sid + ".json"))
                require(digest == cached["capture_sha256"], f"{label}: original hash differs")
                require(source["capture_origin"] == cached["capture_origin"], f"{label}: original URL differs")
                lines = html.unescape(cached["text"]).splitlines()
                for ref in used[sid]:
                    check_line_basis(ref, cached.get("content_type", ""), label, cached["capture_origin"])
                    lo, hi = ref["source_line_start"], ref["source_line_end"]
                    require(hi <= len(lines) and norm(ref["quote"]) in norm("\n".join(lines[lo - 1:hi])),
                            f"{label}: quote absent at stated captured lines")
            counts["sources"] += 1
        counts["topics"] += 1
    require(not any(n > 25 for n in words.values()), "Batch source excerpt budget exceeded")
    require(not args.require_all or not pending, "Unfinished research topics: " + ", ".join(pending))
    if args.require_all:
        unchecked = [slug for slug in selected if cohort[slug].get("research_status") != "evidence_checked"
                     or cohort[slug]["status"] != "ready"]
        require(not unchecked, "Topics still awaiting evidence handoff: " + ", ".join(unchecked))
    print(f"PASS saved research: {counts['topics']} topics; {counts['supported']} source_supported; "
          f"{counts['proposed']} proposed; {counts['sources']} sources; {counts['refs']} located excerpts")
    print("PASS existing Skill contract, per-entry report content/labels/links, capture metadata and batch excerpt budgets")
    if args.cache_dir:
        print("PASS every excerpt matched its actual captured text at the recorded lines")
    if args.baseline:
        print("PASS protected prior outputs, Skill and active catalog are unchanged")
    if args.verify_pinned:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            verified = list(pool.map(verify_pinned_file, pins.items()))
        print(f"PASS live fixed-commit file hashes and excerpt lines: {len(verified)} files")
    print("PENDING:", ", ".join(pending) if pending else "none in the selected topics")
    print("Limits: these checks do not certify semantic support, independent human review or execution.")


if __name__ == "__main__":
    main()

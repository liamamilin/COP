"""Stable ID generation for assembled COP entities.

IDs are deterministic so that re-running the Harness over the same inputs
produces the same references, which keeps diffs between versions meaningful.

Format rules (data model section 4): lowercase, dot-separated, stable within an
artifact lineage, never derived from a display title after creation.
"""

import re
import unicodedata

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")
_TRANSLITERATION = {
    "目标": "goal",
    "流程": "process",
    "阶段": "stage",
    "概念": "concept",
    "操作": "operation",
    "练习": "practice",
    "基础": "foundation",
    "分支": "branch",
}


def slugify(value: str, *, fallback: str = "item") -> str:
    """Convert arbitrary text into a lowercase slug.

    Non-ASCII input is transliterated where a common mapping exists, otherwise
    characters are dropped. The result is always non-empty because callers rely
    on it to build unique entity IDs.
    """
    text = unicodedata.normalize("NFKD", value).strip()
    for source, target in _TRANSLITERATION.items():
        text = text.replace(source, f" {target} ")
    ascii_text = text.encode("ascii", "ignore").decode("ascii").lower()
    slug = _SLUG_STRIP.sub("_", ascii_text).strip("_")
    slug = re.sub(r"_{2,}", "_", slug)
    if len(slug) > 48:
        slug = slug[:48].rstrip("_")
    return slug or fallback


def unique_slug(base: str, taken: set[str]) -> str:
    """Return `base` or `base_2`, `base_3`, ... if already taken."""
    if base not in taken:
        return base
    counter = 2
    while f"{base}_{counter}" in taken:
        counter += 1
    return f"{base}_{counter}"


class IdAllocator:
    """Allocates globally unique entity IDs for one artifact."""

    def __init__(self) -> None:
        self._taken: set[str] = set()

    def reserve(self, candidate: str) -> str:
        self._taken.add(candidate)
        return candidate

    def allocate(self, prefix: str, title: str, *, suffix_parts: tuple[str, ...] = ()) -> str:
        parts = [prefix, *(slugify(part) for part in suffix_parts if part), slugify(title)]
        base = ".".join(part for part in parts if part)
        allocated = unique_slug(base, self._taken)
        self._taken.add(allocated)
        return allocated

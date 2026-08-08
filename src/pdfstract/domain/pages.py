"""Page selection helpers shared by the CLI and the API."""

from __future__ import annotations


def parse_pages(spec: str) -> set[int]:
    """Parse a page spec like '1,3,5-8' into a set of 1-based page numbers."""
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        bounds = part.split("-")
        if len(bounds) not in (1, 2):
            raise ValueError(f"página inválida: {part}")
        try:
            if len(bounds) == 1:
                start = end = int(bounds[0])
            else:
                start, end = int(bounds[0]), int(bounds[1])
        except ValueError as exc:
            raise ValueError(f"página inválida: {part}") from exc
        if start < 1 or end < start:
            raise ValueError(f"intervalo inválido: {part}")
        pages.update(range(start, end + 1))
    if not pages:
        raise ValueError("nenhuma página válida informada")
    return pages


def pages_suffix(pages: set[int]) -> str:
    """Build a compact filename suffix like '_p1,3,5-8' from a set of page numbers."""
    if not pages:
        return ""
    ordered = sorted(pages)
    ranges: list[str] = []
    start = prev = ordered[0]
    for num in ordered[1:]:
        if num == prev + 1:
            prev = num
            continue
        ranges.append(str(start) if start == prev else f"{start}-{prev}")
        start = prev = num
    ranges.append(str(start) if start == prev else f"{start}-{prev}")
    return "_p" + ",".join(ranges)

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
from difflib import SequenceMatcher
import re

from core.scanner import FileEntry, FileInventory
from utils.normalizer import normalize_path, without_extension


@dataclass
class MatchResult:
    found: bool
    matches: list[FileEntry] = field(default_factory=list)


class FileMatcher:
    def __init__(self, inventory: FileInventory, fuzzy_threshold: float = 0.87):
        self.inventory = inventory
        self.fuzzy_threshold = fuzzy_threshold

        # Cache previously matched references
        self._match_cache: dict[str, MatchResult] = {}

    def match(self, reference: str) -> MatchResult:

        query = normalize_path(reference)

        if not query:
            return MatchResult(found=False)

        # Return cached result if available
        cached = self._match_cache.get(query)
        if cached is not None:
            return cached

        candidates: list[FileEntry] = []
        candidates.extend(self.inventory.by_exact.get(query, []))
        candidates.extend(self.inventory.by_no_extension.get(without_extension(query), []))

        query_name = PurePosixPath(query).name
        query_stem = PurePosixPath(without_extension(query)).name
        candidates.extend(self.inventory.by_basename.get(query_name, []))
        candidates.extend(self.inventory.by_stem.get(query_stem, []))

        if "/" in query:
            candidates.extend(self._suffix_matches(query))

        unique = self._unique(candidates)

        if not unique:
            unique = self._fuzzy_matches(query)

        result = MatchResult(
            found=bool(unique),
            matches=unique,
        )

        # Store in cache
        self._match_cache[query] = result

        return result

    def _suffix_matches(self, query: str) -> list[FileEntry]:
        query_no_ext = without_extension(query)
        matches = []
        for entry in self.inventory.entries:
            path = entry.normalized_path
            if path.endswith(query) or without_extension(path).endswith(query_no_ext):
                matches.append(entry)
        return matches

    def _fuzzy_matches(self, query: str) -> list[FileEntry]:
        query_path = PurePosixPath(query)
        query_parent = str(query_path.parent)
        query_suffix = query_path.suffix
        query_stem = PurePosixPath(without_extension(query)).name

        matches: list[tuple[float, FileEntry]] = []
        for entry in self.inventory.entries:
            entry_path = PurePosixPath(entry.normalized_path)
            if query_suffix and entry_path.suffix and query_suffix != entry_path.suffix:
                continue

            if query_parent not in ("", "."):
                entry_parent = str(entry_path.parent)
                if not entry_parent.endswith(query_parent):
                    continue

            score = max(
                SequenceMatcher(None, query_stem, entry.stem).ratio(),
                SequenceMatcher(None, self._fuzzy_key(query_stem), self._fuzzy_key(entry.stem)).ratio(),
                self._token_overlap_score(query_stem, entry.stem),
                self._token_containment_score(query_stem, entry.stem),
            )
            if score >= self.fuzzy_threshold:
                matches.append((score, entry))

        matches.sort(key=lambda item: item[0], reverse=True)
        return [entry for _, entry in matches[:5]]

    @staticmethod
    def _fuzzy_key(value: str) -> str:
        return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))

    @classmethod
    def _token_overlap_score(cls, left: str, right: str) -> float:
        left_tokens = set(cls._fuzzy_key(left).split())
        right_tokens = set(cls._fuzzy_key(right).split())
        if not left_tokens or not right_tokens:
            return 0.0
        return len(left_tokens & right_tokens) / max(len(left_tokens), len(right_tokens))

    @classmethod
    def _token_containment_score(cls, left: str, right: str) -> float:
        left_tokens = cls._meaningful_tokens(left)
        right_tokens = cls._meaningful_tokens(right)
        if not left_tokens or not right_tokens:
            return 0.0
        return len(left_tokens & right_tokens) / min(len(left_tokens), len(right_tokens))

    @classmethod
    def _meaningful_tokens(cls, value: str) -> set[str]:
        return {
            token
            for token in cls._fuzzy_key(value).split()
            if len(token) > 1 and not token.isdigit()
        }

    @staticmethod
    def _unique(entries: list[FileEntry]) -> list[FileEntry]:
        seen: set[str] = set()
        unique: list[FileEntry] = []
        for entry in entries:
            key = entry.display_path.casefold()
            if key in seen:
                continue
            seen.add(key)
            unique.append(entry)
        return unique

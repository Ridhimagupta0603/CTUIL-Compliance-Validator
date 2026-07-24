from __future__ import annotations

import re
import unicodedata
from pathlib import PurePosixPath


BLANK_MARKERS = {
    "",
    "-",
    "--",
    "---",
    "----",
    "-----",
    "/",
    "//",
    "///",
    "////",
    "/////",
    "na",
    "n/a",
    "n.a.",
    "n.a",
    "nil",
    "none",
    "not applicable",
    "not available",
    "not required",
    "blank",
    "no document",
}


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).replace("\u00a0", " ").strip()
    return re.sub(r"\s+", " ", text)


# def is_blank_marker(value: object) -> bool:
#     return normalize_token(clean_text(value)) in BLANK_MARKERS
def is_blank_marker(value) -> bool:

    if value is None:
        return True

    text = clean_text(value).strip().lower()

    if text in BLANK_MARKERS:
        return True

    # Only slashes
    if re.fullmatch(r"[\/\s]+", text):
        return True

    # Only dashes
    if re.fullmatch(r"[-\s]+", text):
        return True

    return False


def normalize_token(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "")
    text = text.replace("\\", "/").strip().strip("\"'")
    text = text.casefold()
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_path(value: str) -> str:
    text = normalize_token(value)
    text = re.sub(r"/+", "/", text).strip("/")
    return text


def without_extension(value: str) -> str:
    normalized = normalize_path(value)
    path = PurePosixPath(normalized)
    name = path.name
    # Treat only a short final dotted token as an extension. Engineering file
    # names often contain dotted numbering like H.3.6.2-33kV, which is not an
    # extension and must remain part of the comparable name.
    if not re.search(r"\.[a-z0-9]{1,8}$", name):
        return normalized
    return str(path.with_suffix(""))


def file_stem(value: str) -> str:
    path = PurePosixPath(normalize_path(value))
    return path.stem if path.suffix else path.name

def split_cell_references(value: object) -> list[str]:

    if value is None:
        return []

    # Preserve newlines
    text = str(value).replace("\u00a0", " ").strip()

    if is_blank_marker(text):
        return []

    # Split on comma, semicolon or any newline
    parts = re.split(r"\s*(?:,|;|\r\n|\r|\n)\s*", text)

    refs = []

    for part in parts:

        part = clean_text(part)

        if part and not is_blank_marker(part):
            refs.append(part)

    return refs
# def split_cell_references(value: object) -> list[str]:
#     text = clean_text(value)

#     if is_blank_marker(text):
#         return []

#     # Split on comma, semicolon or newline.
#     # Ignore spaces before/after separators.
#     parts = re.split(r"\s*(?:,|;|\r\n|\r|\n)\s*", text)

#     refs = [
#         clean_text(part)
#         for part in parts
#         if part and not is_blank_marker(part)
#     ]

#     return refs

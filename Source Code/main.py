from __future__ import annotations

import argparse

from config import (
    DEFAULT_MAX_HEADER_SCAN_ROWS,
    DEFAULT_NESTED_ZIP_LIMIT_MB,
)
from runner import run_validation


def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description="CTUIL Compliance Validator",
    )

    parser.add_argument(
        "workbook",
        help="Compliance Workbook (.xlsx)",
    )

    parser.add_argument(
        "search_roots",
        nargs="+",
        help="Folder(s) and/or ZIP file(s) to search.",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output workbook path.",
    )

    parser.add_argument(
        "--max-header-rows",
        type=int,
        default=DEFAULT_MAX_HEADER_SCAN_ROWS,
    )

    parser.add_argument(
        "--max-nested-zip-mb",
        type=int,
        default=DEFAULT_NESTED_ZIP_LIMIT_MB,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
    )

    parser.add_argument(
        "--no-comments",
        action="store_true",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
    )

    return parser


def main():

    args = build_parser().parse_args()

    result = run_validation(
        workbook_path=args.workbook,
        search_roots=args.search_roots,
        output_path=args.output,
        max_header_rows=args.max_header_rows,
        max_nested_zip_mb=args.max_nested_zip_mb,
        dry_run=args.dry_run,
        no_comments=args.no_comments,
        verbose=args.verbose,
    )

    print("\nValidation Completed Successfully\n")

    print(f"Detected Columns : {result['detected_columns']}")
    print(f"Checked Cells    : {result['checked_cells']}")
    print(f"Missing Cells    : {result['missing_cells']}")

    if result["saved"] is not None:
        print(f"\nOutput Workbook : {result['saved']}")


if __name__ == "__main__":
    main()
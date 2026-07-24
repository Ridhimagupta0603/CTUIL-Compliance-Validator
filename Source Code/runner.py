from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from config import (
    DEFAULT_MAX_HEADER_SCAN_ROWS,
    DEFAULT_NESTED_ZIP_LIMIT_MB,
    default_output_path,
)

from core.matcher import FileMatcher
from core.scanner import FileScanner
from core.validator import ComplianceValidator
from core.workbook import WorkbookInspector
from core.writer import WorkbookWriter

from utils.logger import configure_logging


def run_validation(
    workbook_path: str | Path,
    search_roots: list[str | Path],
    output_path: str | Path | None = None,
    *,
    max_header_rows: int = DEFAULT_MAX_HEADER_SCAN_ROWS,
    max_nested_zip_mb: int = DEFAULT_NESTED_ZIP_LIMIT_MB,
    dry_run: bool = False,
    no_comments: bool = False,
    verbose: bool = False,
    progress_callback: Callable[[str, int], None] | None = None,
) -> dict:
    """
    Runs the complete compliance validation.

    Returns a dictionary containing validation statistics.
    """

    def update(status: str, progress: int):
        logging.info(status)
        if progress_callback:
            progress_callback(status, progress)

    configure_logging(verbose)

    workbook_path = Path(workbook_path)

    if output_path:
        output_path = Path(output_path)
    else:
        output_path = default_output_path(workbook_path)

    ############################################################
    # Scan submitted files
    ############################################################

    update("Scanning submitted files...", 10)

    inventory = FileScanner(
        search_roots,
        max_nested_zip_mb=max_nested_zip_mb,
    ).scan()

    ############################################################
    # Load workbook
    ############################################################

    update("Loading workbook...", 25)

    inspector = WorkbookInspector(
        workbook_path,
        max_header_scan_rows=max_header_rows,
    )

    wb = inspector.load()

    ############################################################
    # Detect filename columns
    ############################################################

    update("Detecting filename columns...", 40)

    filename_columns = inspector.find_filename_columns(wb)

    if not filename_columns:
        raise RuntimeError(
            "No filename/document/folder columns were detected."
        )

    ############################################################
    # Validate
    ############################################################

    update("Validating workbook...", 65)

    matcher = FileMatcher(inventory)

    validator = ComplianceValidator(matcher)

    validations = validator.validate(
        wb,
        filename_columns,
    )

    checked_cells = sum(
        len(v.results)
        for v in validations
    )

    missing_cells = sum(
        1
        for validation in validations
        for result in validation.results
        if result.status == "No"
    )

    ############################################################
    # Dry Run
    ############################################################

    if dry_run:

        update("Dry Run Complete", 100)

        return {
            "saved": None,
            "checked_cells": checked_cells,
            "missing_cells": missing_cells,
            "detected_columns": len(filename_columns),
        }

    ############################################################
    # Save workbook
    ############################################################

    update("Writing validated workbook...", 90)

    writer = WorkbookWriter(
        add_comments=not no_comments,
    )

    saved = writer.write(
        wb,
        validations,
        output_path,
    )

    ############################################################
    # Finished
    ############################################################

    update("Completed", 100)

    return {
        "saved": saved,
        "checked_cells": checked_cells,
        "missing_cells": missing_cells,
        "detected_columns": len(filename_columns),
    }
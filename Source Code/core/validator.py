from __future__ import annotations

from dataclasses import dataclass, field

from openpyxl.workbook.workbook import Workbook

from core.matcher import FileMatcher
from core.workbook import FilenameColumn
from utils.normalizer import is_blank_marker, split_cell_references


@dataclass(frozen=True)
class CellValidation:
    row: int
    source_column: int
    status: str
    references: tuple[str, ...]
    matched_paths: tuple[str, ...] = field(default_factory=tuple)
    missing_references: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ColumnValidation:
    filename_column: FilenameColumn
    results: tuple[CellValidation, ...]


class ComplianceValidator:
    def __init__(self, matcher: FileMatcher):
        self.matcher = matcher

    def validate(self, wb: Workbook, filename_columns: list[FilenameColumn]) -> list[ColumnValidation]:
        validations: list[ColumnValidation] = []
        for filename_column in filename_columns:
            ws = wb[filename_column.sheet_name]
            results = self._validate_column(ws, filename_column)
            validations.append(ColumnValidation(filename_column=filename_column, results=tuple(results)))
        return validations

    def _validate_column(self, ws, filename_column: FilenameColumn) -> list[CellValidation]:
        results: list[CellValidation] = []
        for row_idx in range(filename_column.header_row + 1, ws.max_row + 1):
            cell = ws.cell(row=row_idx, column=filename_column.column)
            if is_blank_marker(cell.value):
                continue

            references = split_cell_references(cell.value)

            # Blank markers like /////, NA, N/A, -, etc.
            # should not be validated.
            # Skip placeholders like /////, NA, N/A, -, etc.
            if not references:
                results.append(
                    CellValidation(
                        row=row_idx,
                        source_column=filename_column.column,
                        status="",                 # Leave validation blank
                        references=(),
                        matched_paths=(),
                        missing_references=(),
                    )
                )
                continue

            matched_paths: list[str] = []
            missing: list[str] = []
            for reference in references:
                match = self.matcher.match(reference)
                if match.found:
                    matched_paths.extend(entry.display_path for entry in match.matches[:5])
                else:
                    missing.append(reference)
                 

            status = "Yes" if not missing else "No"
            results.append(
                CellValidation(
                    row=row_idx,
                    source_column=filename_column.column,
                    status=status,
                    references=tuple(references),
                    matched_paths=tuple(dict.fromkeys(matched_paths)),
                    missing_references=tuple(missing),
                )
            )
        return results

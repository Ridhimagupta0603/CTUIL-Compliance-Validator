# CTUIL Compliance Validator EXE FILE README

## Overview

CTUIL Compliance Validator is a desktop application that validates document references in a CTUIL Compliance Validation Excel workbook against the submitted folders and ZIP files. It generates a new workbook with **Yes/No** validation results for each document reference.

---

## How to Use

1. Launch **CTUIL Compliance Validator.exe**.
2. Select the **Compliance Workbook (.xlsx)**.
3. Add one or more **Submission Folders** and/or **ZIP Files**.
4. Choose the **Output Workbook** location (or use the default suggested path).
5. Click **Start Validation**. Open in full Dialogue box if button not visible.

The application will scan all selected files, validate the document references, and generate a validated Excel workbook.

---

## Output

The generated workbook includes:

* A validation column beside each detected filename/document column.
* **Yes** if all referenced files are found.
* **No** if one or more referenced files are missing.
* Optional comments showing matched and missing file paths (unless **No Comments** is selected).

---
## Key Features
* Validates document references in the CONN-4 Compliance Validation workbook.
* Supports both submission folders and ZIP files (including nested ZIP files).
* Automatically detects document/filename columns across all worksheets.
* Supports:
  1. Single document references
  2. Multiple document references separated by commas or line breaks
* Generates a new validated workbook without modifying the original file.
* Adds:
  1. CTUIL Validation Status (Yes/No)
  2. CTUIL Validation Remarks, indicating missing document references where applicable.
* Ignores non-document placeholders such as NA, N/A, /////, etc.
* Simple GUI (graphical user interface) with no command-line operation required.
* The GitHub repository containing the complete source code as well as the EXE file is also available for reference and future enhancements at https://github.com/Ridhimagupta0603/CTUIL-Compliance-Validator
## Notes

* Supports multiple folders and ZIP files.
* Supports nested ZIP files.
* Original workbook is not modified.
* A new validated workbook is created at the selected output location.

---

## Requirements

* Windows 10 or later
* Microsoft Excel workbook (.xlsx)
* No Python installation is required to run the executable.

---

**Version:** 1.0 Ridhima Gupta ©

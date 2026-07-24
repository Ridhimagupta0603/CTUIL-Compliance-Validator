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

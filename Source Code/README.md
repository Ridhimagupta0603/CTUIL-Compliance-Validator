# CTUIL Compliance Validator

Validates filename, document name, and folder name references in a CTUIL compliance
validation workbook against submitted folders and zip files.

## Install

```powershell 
cd "C:\Users\yourUsername\Desktop\CTUIL\1 My Work\Complaince Sheet Verifier\ComplianceValidator"
py -m pip install -r requirements.txt
```

## Run to open GUI
```powershell
py gui.py
```
## Run main.py with below command prompt to validate from Terminal without GUI
```powershell
py main.py "..\CON4_Compliance_Validation_Sheet.xlsx" "..\Folderpath" -o "..\CON4_Compliance_Validation_Sheet_validated.xlsx"
```
You can pass multiple search roots:

```powershell
py gui.py
```
#For running main.py without GUI
```powershell
py main.py "..\CON4_Compliance_Validation_Sheet.xlsx" "D:\SubmissionFolder" "D:\Submission.zip"
```
## What It Does

- Scans folders, zip files, and nested zip files.
- Detects filename-like headers across all workbook sheets, even when columns are
  hidden or located at different positions.
- Handles examples such as `File Name(pdf)`, `File Name(PSSE/PSCAD)`,
  `Document Name`, `Name of File/ Folder Name`, and `Ref Document Name`.
- Matches case-insensitively and supports:
  - `filename.extension`
  - `folder\filename.extension`
  - `folder\filename`
  - `filename`
- Adds one `Found? - <header>` status column beside each detected filename column.
- Writes `Yes` only when all references in that cell are found; otherwise writes
  `No`.
- Adds comments showing matched and missing paths unless `--no-comments` is used.
- Adds Remarks column showing matched and missing paths.


Use `--dry-run` to check detected columns without writing an output workbook.

# Convert2MD

Convert supported documents into Markdown files using Microsoft's
[MarkItDown](https://github.com/microsoft/markitdown). The script can process
all supported files in a folder or a list of files you select. It writes the
results as UTF-8 `.md` files and can use local Tesseract OCR for scanned PDFs
that contain no extractable text.

## Requirements

- Python 3.10 or later
- The Python packages in [`requirements.txt`](requirements.txt)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) only if you need
  OCR for scanned/image-only PDFs

MarkItDown and its optional format integrations may have additional system
requirements for particular file types.

## Installation

Clone the repository and install its Python dependencies:

```powershell
git clone https://github.com/saigonson/Convert2MD.git
cd Convert2MD
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell prevents activation, you can run the environment's Python
directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Quick start

Put the documents you want to convert in a folder. From that folder, run the
script by its path:

```powershell
cd "C:\path\to\your\documents"
& "C:\path\to\Convert2MD\.venv\Scripts\python.exe" "C:\path\to\Convert2MD\convert_to_md.py"
```

The script scans only the current folder (not subfolders). Converted Markdown
files are written to a `markdown_outputs` subfolder, which is created if
necessary. For example:

```text
your-documents\
├── report.pdf
├── presentation.pptx
└── markdown_outputs\
    ├── report.md
    └── presentation.md
```

To use a different Python environment, replace the virtual-environment Python
path in the command with the path to that environment's interpreter.

## Supported input formats

The script accepts these file extensions (case-insensitively):

| Type | Extensions |
| --- | --- |
| PDF | `.pdf` |
| Word | `.docx` |
| PowerPoint | `.pptx` |
| Excel | `.xlsx`, `.xls` |
| Data and text | `.csv`, `.txt`, `.json`, `.xml` |
| Web pages | `.html`, `.htm` |
| Email | `.eml`, `.msg` |

Conversion is performed by MarkItDown. The amount and formatting of extracted
content depend on the input file and MarkItDown's support for its format.
Legacy or specialized formats may require additional MarkItDown dependencies.

## Scanned PDF OCR

For a PDF with no embedded text, the script attempts local OCR:

1. Install Tesseract OCR and make `tesseract` available on `PATH`. On Windows,
   the script also checks the `Tesseract-OCR\tesseract.exe` location under
   `Program Files` and `Program Files (x86)`.
2. Install the Python dependencies as described above.
3. Run the script as usual. It renders PDF pages locally and sends each page
   image to Tesseract for text recognition.

Tesseract is needed only for scanned PDFs with no text extracted by
MarkItDown. It is not installed by `requirements.txt`. OCR quality depends on
the scan and Tesseract; this project does not perform OCR on other formats.

## Use from Python

You can call `convert_files_to_markdown` from another Python script:

```python
from convert_to_md import convert_files_to_markdown

convert_files_to_markdown(
    source_paths=[
        r"C:\path\to\documents\report.pdf",
        r"C:\path\to\documents\notes.docx",
    ],
    output_dir=r"C:\path\to\markdown_outputs",
)
```

`source_paths` is an optional list of file paths. When omitted (or set to
`None`), the function discovers supported files directly inside the current
working directory. `output_dir` defaults to `markdown_outputs`; relative
output paths are resolved from the current working directory. The function
creates the output directory if it does not exist.

## What the script does

- Finds supported files in the current folder, sorted by file name, when no
  explicit input list is supplied.
- Skips unsupported paths and Microsoft Office temporary/lock files whose
  names start with `~$`.
- Converts each supported input and writes the extracted text to a UTF-8
  Markdown file named after the input file (for example, `report.pdf` becomes
  `report.md`).
- If a PDF conversion returns no text, renders its pages and runs Tesseract
  OCR locally.
- Prints a status message for each conversion. A per-file error is printed
  and processing continues with the next input.

### Notes and limitations

- Folder discovery is not recursive. Files inside nested folders are not
  automatically found.
- If two inputs have the same file name stem, they target the same Markdown
  output path; the later successful conversion overwrites the earlier file.
- Inputs that produce no text are reported as failures and do not produce an
  output file.
- The script reports per-file failures in its console output; check those
  messages to confirm which files converted successfully.

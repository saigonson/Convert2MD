import os
import shutil
import subprocess
from io import BytesIO
from pathlib import Path

from markitdown import MarkItDown
import pypdfium2 as pdfium


def _find_tesseract() -> Path:
    executable = shutil.which("tesseract")
    if executable:
        return Path(executable)

    for program_files in (
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
    ):
        if program_files:
            candidate = Path(program_files) / "Tesseract-OCR" / "tesseract.exe"
            if candidate.is_file():
                return candidate

    raise FileNotFoundError(
        "Tesseract OCR is required for scanned PDFs. Install Tesseract and "
        "add it to PATH, or install it under Program Files."
    )


def _ocr_pdf(file_path: Path) -> str:
    tesseract = _find_tesseract()
    pdf = pdfium.PdfDocument(str(file_path))
    page_text = []

    for page_number in range(len(pdf)):
        page = pdf[page_number]
        image = page.render(scale=2).to_pil()
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")
        result = subprocess.run(
            [str(tesseract), "stdin", "stdout"],
            input=image_bytes.getvalue(),
            capture_output=True,
            check=True,
        )
        page_text.append(result.stdout.decode("utf-8").strip())

    return "\n\n".join(text for text in page_text if text)


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".xls",
    ".csv",
    ".html",
    ".htm",
    ".txt",
    ".json",
    ".xml",
    ".eml",
    ".msg",
}


def _is_supported_file(file_path: Path) -> bool:
    return (
        file_path.is_file()
        and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
        and not file_path.name.lower().startswith("~$")
    )


def _find_supported_files(folder: Path, output_dir_name: str = "markdown_outputs") -> list[Path]:
    folder = folder.resolve()
    output_dir = (folder / output_dir_name).resolve()
    file_paths = []

    for path in sorted(folder.iterdir()):
        if path.is_dir() and path.resolve() == output_dir:
            continue
        if _is_supported_file(path):
            file_paths.append(path)

    return file_paths


def convert_files_to_markdown(
    source_paths: list[str] | None = None,
    output_dir: str = "markdown_outputs",
) -> None:
    """Convert supported files in the current folder to Markdown files in markdown_outputs."""
    source_folder = Path.cwd()
    output_path = Path(output_dir)
    if not output_path.is_absolute():
        output_path = source_folder / output_path

    output_path.mkdir(parents=True, exist_ok=True)

    if source_paths is None:
        source_paths = [str(path) for path in _find_supported_files(source_folder, output_dir)]

    if not source_paths:
        print(f"[i] No supported files were found in {source_folder}.")
        return

    converter = MarkItDown()

    for file_str in source_paths:
        file_path = Path(file_str)

        if not _is_supported_file(file_path):
            print(f"[x] Unsupported or skipped file: {file_path}")
            continue

        if output_path.resolve() == file_path.resolve().parent:
            print(f"[x] Skipping file already inside the output folder: {file_path}")
            continue

        try:
            result = converter.convert(str(file_path))
            text_content = result.text_content

            if not text_content.strip() and file_path.suffix.lower() == ".pdf":
                print(f"[i] No embedded text in {file_path.name}; running local OCR.")
                text_content = _ocr_pdf(file_path)

            if not text_content.strip():
                raise ValueError("Conversion produced no text; no Markdown file was written.")

            target_md_path = output_path / f"{file_path.stem}.md"
            target_md_path.write_text(text_content, encoding="utf-8")

            print(f"[+] Converted: {file_path.name} -> {target_md_path}")

        except Exception as e:
            print(f"[!] Failed to convert {file_path.name}: {e}")


if __name__ == "__main__":
    convert_files_to_markdown()
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types


ROOT = Path(__file__).resolve().parent
ENTRIES_DIR = ROOT / "entries"
README_PATH = ROOT / "README.md"
LOG_PATH = ROOT / "daily-ai.log"

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.1-flash-lite",
)

ALLOWED_LANGUAGES = {
    "python": "py",
    "sql": "sql",
}

TOPICS = [
    "Python command-line utility",
    "Python file-processing utility",
    "Python CSV data-processing utility",
    "Python JSON data-processing utility",
    "Python text parsing and validation utility",
    "Python date and time utility",
    "Python data-cleaning utility",
    "Python local automation helper",
    "Python log-file analysis utility",
    "Python filesystem organization utility",
    "SQL Server reporting query",
    "SQL Server data-cleaning query",
    "SQL Server duplicate detection query",
    "SQL Server date-based reporting query",
    "SQL Server aggregation and analysis query",
    "SQL Server validation query",
    "SQL Server reconciliation query",
    "SQL Server XML-processing query",
    "SQL Server data-quality audit query",
]


def log(message: str) -> None:
    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    line = f"[{timestamp}] {message}"

    print(line)

    with LOG_PATH.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(line + "\n")


def run_git(
    *args: str,
    capture: bool = True,
) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=capture,
        check=False,
    )

    if result.returncode != 0:
        error = (
            result.stderr.strip()
            if capture
            else ""
        )

        raise RuntimeError(
            "Git komutu basarisiz: "
            f"git {' '.join(args)}\n"
            f"{error}"
        )

    if capture:
        return result.stdout.strip()

    return ""


def extract_json(
    text: str,
) -> dict[str, Any]:
    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    try:
        data = json.loads(text)

    except json.JSONDecodeError:
        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL,
        )

        if not match:
            raise ValueError(
                "Model cevabinda JSON bulunamadi."
            )

        try:
            data = json.loads(
                match.group(0)
            )

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Model gecersiz JSON uretti: "
                f"{exc}"
            ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "Model cevabi JSON nesnesi olmali."
        )

    return data


def safe_slug(
    title: str,
) -> str:
    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        title.lower(),
    ).strip("-")

    return slug[:70] or "daily-entry"


def normalize_text(
    value: str,
) -> set[str]:
    words = re.findall(
        r"[a-z0-9]+",
        value.lower(),
    )

    ignored_words = {
        "a",
        "an",
        "and",
        "as",
        "by",
        "for",
        "from",
        "in",
        "into",
        "of",
        "on",
        "or",
        "the",
        "to",
        "using",
        "with",
        "utility",
        "tool",
        "helper",
        "script",
        "example",
        "python",
        "sql",
        "server",
        "data",
    }

    return {
        word
        for word in words
        if word not in ignored_words
        and len(word) >= 3
    }


def read_entry_summary(
    readme_path: Path,
) -> dict[str, str] | None:
    try:
        content = readme_path.read_text(
            encoding="utf-8",
        )

    except OSError:
        return None

    title_match = re.search(
        r"^#\s+(.+)$",
        content,
        re.MULTILINE,
    )

    description_match = re.search(
        r"## Description\s+(.+?)(?:\n##|\Z)",
        content,
        re.DOTALL,
    )

    language_match = re.search(
        r"\*\*Language:\*\*\s*(.+)",
        content,
    )

    title = (
        title_match.group(1).strip()
        if title_match
        else readme_path.parent.name
    )

    description = (
        " ".join(
            description_match.group(1).split()
        )
        if description_match
        else "No description available."
    )

    language = (
        language_match.group(1).strip()
        if language_match
        else "Unknown"
    )

    return {
        "date": readme_path.parent.name,
        "title": title,
        "description": description,
        "language": language,
    }


def get_previous_entries(
    limit: int = 100,
) -> list[dict[str, str]]:
    if not ENTRIES_DIR.exists():
        return []

    readme_files = sorted(
        ENTRIES_DIR.glob("*/README.md"),
        key=lambda path: path.parent.name,
        reverse=True,
    )

    previous_entries: list[dict[str, str]] = []

    for readme_path in readme_files[:limit]:
        summary = read_entry_summary(
            readme_path
        )

        if summary:
            previous_entries.append(
                summary
            )

    return previous_entries


def format_previous_entries(
    entries: list[dict[str, str]],
) -> str:
    if not entries:
        return (
            "No previous repository entries exist yet."
        )

    lines: list[str] = []

    for entry in entries:
        lines.append(
            f"- {entry['date']} | "
            f"{entry['language']} | "
            f"{entry['title']} | "
            f"{entry['description']}"
        )

    return "\n".join(lines)


def calculate_similarity(
    first: str,
    second: str,
) -> float:
    first_words = normalize_text(first)
    second_words = normalize_text(second)

    if not first_words or not second_words:
        return 0.0

    intersection = (
        first_words & second_words
    )

    union = (
        first_words | second_words
    )

    if not union:
        return 0.0

    return len(intersection) / len(union)


def ensure_unique_entry(
    data: dict[str, str],
    previous_entries: list[dict[str, str]],
) -> None:
    new_text = (
        f"{data['title']} "
        f"{data['description']} "
        f"{data['usage']}"
    )

    for previous in previous_entries:
        previous_text = (
            f"{previous['title']} "
            f"{previous['description']}"
        )

        similarity = calculate_similarity(
            new_text,
            previous_text,
        )

        if similarity >= 0.45:
            raise RuntimeError(
                "Uretilen kayit onceki bir kayda "
                "fazla benziyor.\n"
                f"Yeni baslik: {data['title']}\n"
                f"Benzer kayit: "
                f"{previous['title']} "
                f"({previous['date']})\n"
                f"Benzerlik: %{similarity * 100:.1f}\n"
                "Scripti tekrar calistirarak "
                "farkli bir fikir urettirebilirsin."
            )


def generate_entry() -> dict[str, str]:
    load_dotenv(
        ROOT / ".env",
        encoding="utf-8-sig",
        override=True,
    )

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            ".env icinde GEMINI_API_KEY "
            "bulunamadi."
        )

    model = os.getenv(
        "GEMINI_MODEL",
        MODEL,
    ).strip()

    day_index = (
        datetime.now().toordinal()
        % len(TOPICS)
    )

    topic = TOPICS[day_index]

    previous_entries = (
        get_previous_entries()
    )

    previous_entries_text = (
        format_previous_entries(
            previous_entries
        )
    )

    client = genai.Client(
        api_key=api_key
    )

    prompt = f"""
Create one small, original and genuinely useful programming example.

Today's preferred category:
{topic}

The repository already contains these entries:

{previous_entries_text}

Uniqueness rules:
- Do not repeat any previous entry.
- Do not create a renamed version of a previous entry.
- Do not create a utility with substantially the same purpose.
- Compare purpose, inputs, outputs and implementation concept.
- If today's preferred category would cause duplication, choose another Python or SQL idea.
- Prefer a clearly different real-world problem.
- The new entry must add meaningful variety to the repository.

Language rules:
- The language must be either python or sql.
- For SQL, use Microsoft SQL Server syntax.
- Do not generate JavaScript, TypeScript, PowerShell or other languages.

General rules:
- Return only valid JSON.
- Do not use Markdown code fences.
- Do not include text outside the JSON object.
- Keep the source code roughly between 20 and 120 lines.
- The example must be complete and understandable.
- Python examples should preferably use only the standard library.
- Do not access external APIs or network services.
- Include reasonable validation or error handling.
- Do not generate filler content.
- Do not generate malware, credential harvesting, spam or destructive code.
- Use English for title, description, usage and code comments.
- Avoid hello world, calculators, number guessing and similarly trivial examples.
- SQL examples should focus on reporting, validation, reconciliation, auditing, XML processing or data cleaning.
- SQL examples should include sample table assumptions as comments where useful.
- Python examples should include a main function or clear usage entry point where appropriate.

JSON schema:
{{
  "title": "Unique descriptive title",
  "language": "python",
  "description": "One-sentence description",
  "usage": "Brief usage instructions",
  "code": "Complete source code"
}}
"""

    log(
        "Gemini istegi gonderiliyor. "
        f"Model: {model}"
    )

    try:
        response = (
            client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.95,
                    response_mime_type=(
                        "application/json"
                    ),
                ),
            )
        )

    finally:
        client.close()

    response_text = response.text

    if not response_text:
        raise RuntimeError(
            "Gemini bos cevap dondurdu."
        )

    data = extract_json(
        response_text
    )

    required = {
        "title",
        "language",
        "description",
        "usage",
        "code",
    }

    missing = required.difference(
        data
    )

    if missing:
        raise ValueError(
            "Eksik model alanlari: "
            + ", ".join(
                sorted(missing)
            )
        )

    cleaned = {
        key: str(data[key]).strip()
        for key in required
    }

    language = (
        cleaned["language"]
        .lower()
        .strip()
    )

    if language in {
        "python3",
        "python 3",
        "py",
    }:
        language = "python"

    if language in {
        "sql server",
        "mssql",
        "t-sql",
        "tsql",
    }:
        language = "sql"

    if language not in ALLOWED_LANGUAGES:
        raise ValueError(
            "Desteklenmeyen dil: "
            f"{language}. "
            "Sadece Python ve SQL kabul edilir."
        )

    if not cleaned["title"]:
        raise ValueError(
            "Model bos baslik uretti."
        )

    if not cleaned["description"]:
        raise ValueError(
            "Model bos aciklama uretti."
        )

    if not cleaned["usage"]:
        raise ValueError(
            "Model bos kullanim aciklamasi uretti."
        )

    if not cleaned["code"]:
        raise ValueError(
            "Model bos kod uretti."
        )

    line_count = len(
        cleaned["code"].splitlines()
    )

    if line_count < 10:
        raise ValueError(
            "Uretilen kod cok kisa: "
            f"{line_count} satir."
        )

    if line_count > 180:
        raise ValueError(
            "Uretilen kod izin verilen "
            "uzunlugu asti: "
            f"{line_count} satir."
        )

    cleaned["language"] = language

    ensure_unique_entry(
        cleaned,
        previous_entries,
    )

    return cleaned


def ensure_clean_repository() -> None:
    status = run_git(
        "status",
        "--porcelain",
    )

    ignored_prefixes = {
        "?? .env",
        "?? .venv",
        "?? daily-ai.log",
    }

    relevant_lines = [
        line
        for line in status.splitlines()
        if line
        and not any(
            line.startswith(prefix)
            for prefix in ignored_prefixes
        )
    ]

    if relevant_lines:
        raise RuntimeError(
            "Repoda commit edilmemis "
            "degisiklikler var. "
            "Once bunlari commit et veya geri al:\n"
            + "\n".join(relevant_lines)
        )


def create_entry(
    data: dict[str, str],
) -> Path:
    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    day_dir = ENTRIES_DIR / today

    if (
        day_dir.exists()
        and any(day_dir.iterdir())
    ):
        raise RuntimeError(
            f"{today} icin zaten bir "
            "kayit olusturulmus."
        )

    day_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    extension = ALLOWED_LANGUAGES[
        data["language"]
    ]

    code_path = (
        day_dir
        / (
            f"{safe_slug(data['title'])}"
            f".{extension}"
        )
    )

    notes_path = (
        day_dir / "README.md"
    )

    code_path.write_text(
        data["code"].rstrip() + "\n",
        encoding="utf-8",
    )

    notes_path.write_text(
        f"""# {data["title"]}

**Date:** {today}  
**Language:** {data["language"].title()}

## Description

{data["description"]}

## Usage

{data["usage"]}
""",
        encoding="utf-8",
    )

    return code_path


def update_readme(
    data: dict[str, str],
    code_path: Path,
) -> None:
    marker = "<!-- DAILY_ENTRIES -->"

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    relative_path = (
        code_path
        .relative_to(ROOT)
        .as_posix()
    )

    row = (
        f"| {today} "
        f"| [{data['title']}]"
        f"({relative_path}) "
        f"| {data['language'].title()} "
        f"| {data['description']} |\n"
    )

    if README_PATH.exists():
        content = README_PATH.read_text(
            encoding="utf-8",
        )

    else:
        content = ""

    if marker not in content:
        content = f"""# Daily Dev

A collection of small Python and SQL utilities and experiments.

| Date | Entry | Language | Description |
|---|---|---|---|
{marker}
"""

    content = content.replace(
        marker,
        row + marker,
        1,
    )

    README_PATH.write_text(
        content,
        encoding="utf-8",
    )


def commit_and_push(
    data: dict[str, str],
) -> None:
    run_git(
        "add",
        "entries",
        "README.md",
        ".gitignore",
    )

    staged = run_git(
        "diff",
        "--cached",
        "--name-only",
    )

    if not staged:
        log(
            "Commit edilecek degisiklik "
            "bulunamadi."
        )
        return

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    message = (
        f"Add {data['title']} "
        f"({today})"
    )

    run_git(
        "commit",
        "-m",
        message,
    )

    branch = run_git(
        "branch",
        "--show-current",
    )

    if not branch:
        raise RuntimeError(
            "Aktif Git branch'i "
            "bulunamadi."
        )

    run_git(
        "push",
        "origin",
        branch,
    )

    log(
        "GitHub'a gonderildi: "
        f"{message}"
    )


def main() -> int:
    try:
        ensure_clean_repository()

        entry = generate_entry()

        code_path = create_entry(
            entry
        )

        update_readme(
            entry,
            code_path,
        )

        commit_and_push(
            entry
        )

        log(
            "Olusturulan dosya: "
            f"{code_path.relative_to(ROOT)}"
        )

        return 0

    except Exception as exc:
        log(
            f"HATA: {exc}"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
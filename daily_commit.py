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
from openai import OpenAI


ROOT = Path(__file__).resolve().parent
ENTRIES_DIR = ROOT / "entries"
README_PATH = ROOT / "README.md"
LOG_PATH = ROOT / "daily-ai.log"

MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

ALLOWED_LANGUAGES = {
    "python": "py",
    "javascript": "js",
    "typescript": "ts",
    "sql": "sql",
    "powershell": "ps1",
}

TOPICS = [
    "Python command-line utility",
    "SQL reporting or data-cleaning example",
    "JavaScript data-processing helper",
    "TypeScript validation utility",
    "PowerShell Windows automation helper",
    "RPG Maker MV JavaScript utility",
    "text parsing tool",
    "date and time helper",
    "CSV or JSON processing utility",
    "small algorithm with practical usage",
]


def log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(line + "\n")


def run_git(*args: str, capture: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=capture,
        check=False,
    )

    if result.returncode != 0:
        error = result.stderr.strip() if capture else ""
        raise RuntimeError(f"Git komutu basarisiz: git {' '.join(args)}\n{error}")

    return result.stdout.strip() if capture else ""


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("Model cevabinda JSON bulunamadi.")
        data = json.loads(match.group(0))

    if not isinstance(data, dict):
        raise ValueError("Model cevabi JSON nesnesi olmali.")

    return data


def safe_slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:70] or "daily-entry"


def generate_entry() -> dict[str, str]:
    load_dotenv(ROOT / ".env")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(".env icinde OPENAI_API_KEY bulunamadi.")

    day_index = datetime.now().toordinal() % len(TOPICS)
    topic = TOPICS[day_index]

    client = OpenAI(api_key=api_key)

    prompt = f"""
Create one small, original and genuinely useful programming example.

Today's topic: {topic}

Rules:
- Return only valid JSON, without Markdown fences.
- Language must be one of: python, javascript, typescript, sql, powershell.
- Keep the source code roughly between 20 and 120 lines.
- The example must be complete and understandable.
- Prefer standard libraries and no external network access.
- Include reasonable validation or error handling.
- Do not generate filler, malware, credential harvesting, spam, or destructive code.
- Use English for title, description, usage and code comments.
- Avoid duplicating common trivial examples such as hello world or basic calculators.

JSON schema:
{{
  "title": "Unique descriptive title",
  "language": "python",
  "description": "One-sentence description",
  "usage": "Brief usage instructions",
  "code": "Complete source code"
}}
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    data = extract_json(response.output_text)

    required = {"title", "language", "description", "usage", "code"}
    missing = required.difference(data)

    if missing:
        raise ValueError(f"Eksik model alanlari: {', '.join(sorted(missing))}")

    cleaned = {key: str(data[key]).strip() for key in required}
    language = cleaned["language"].lower()

    if language not in ALLOWED_LANGUAGES:
        raise ValueError(f"Desteklenmeyen dil: {language}")

    if not cleaned["code"]:
        raise ValueError("Model bos kod uretti.")

    if len(cleaned["code"].splitlines()) > 180:
        raise ValueError("Uretilen kod izin verilen uzunlugu asti.")

    cleaned["language"] = language
    return cleaned


def ensure_clean_repository() -> None:
    status = run_git("status", "--porcelain")

    ignored_prefixes = {
        "?? .env",
        "?? .venv",
        "?? daily-ai.log",
    }

    relevant_lines = [
        line for line in status.splitlines()
        if line and not any(line.startswith(prefix) for prefix in ignored_prefixes)
    ]

    if relevant_lines:
        raise RuntimeError(
            "Repoda commit edilmemis degisiklikler var. Once bunlari commit et veya geri al:\n"
            + "\n".join(relevant_lines)
        )


def create_entry(data: dict[str, str]) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    day_dir = ENTRIES_DIR / today

    if day_dir.exists() and any(day_dir.iterdir()):
        raise RuntimeError(f"{today} icin zaten bir kayit olusturulmus.")

    day_dir.mkdir(parents=True, exist_ok=True)

    extension = ALLOWED_LANGUAGES[data["language"]]
    code_path = day_dir / f"{safe_slug(data['title'])}.{extension}"
    notes_path = day_dir / "README.md"

    code_path.write_text(data["code"].rstrip() + "\n", encoding="utf-8")

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


def update_readme(data: dict[str, str], code_path: Path) -> None:
    marker = "<!-- DAILY_ENTRIES -->"
    today = datetime.now().strftime("%Y-%m-%d")
    relative_path = code_path.relative_to(ROOT).as_posix()

    row = (
        f"| {today} | [{data['title']}]({relative_path}) | "
        f"{data['language'].title()} | {data['description']} |\n"
    )

    if README_PATH.exists():
        content = README_PATH.read_text(encoding="utf-8")
    else:
        content = ""

    if marker not in content:
        content = f"""# Daily Dev

A collection of small programming utilities and experiments.

| Date | Entry | Language | Description |
|---|---|---|---|
{marker}
"""

    content = content.replace(marker, row + marker, 1)
    README_PATH.write_text(content, encoding="utf-8")


def commit_and_push(data: dict[str, str]) -> None:
    run_git("add", "entries", "README.md", ".gitignore")

    staged = run_git("diff", "--cached", "--name-only")
    if not staged:
        log("Commit edilecek degisiklik bulunamadi.")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    message = f"feat: add daily entry - {data['title']} ({today})"

    run_git("commit", "-m", message)
    branch = run_git("branch", "--show-current")

    if not branch:
        raise RuntimeError("Aktif Git branch'i bulunamadi.")

    run_git("push", "origin", branch)
    log(f"GitHub'a gonderildi: {message}")


def main() -> int:
    try:
        ensure_clean_repository()
        entry = generate_entry()
        code_path = create_entry(entry)
        update_readme(entry, code_path)
        commit_and_push(entry)
        log(f"Olusturulan dosya: {code_path.relative_to(ROOT)}")
        return 0
    except Exception as exc:
        log(f"HATA: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

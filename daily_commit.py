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

# .env içerisinde GEMINI_MODEL tanımlanırsa onu kullanır.
# Tanımlanmazsa varsayılan model kullanılır.
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

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

        raise RuntimeError(
            f"Git komutu basarisiz: git {' '.join(args)}\n{error}"
        )

    return result.stdout.strip() if capture else ""


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()

    # Gemini bazen JSON'u Markdown kod blogu içerisinde döndürebilir.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            raise ValueError("Model cevabinda JSON bulunamadi.")

        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Model gecersiz JSON uretti: {exc}"
            ) from exc

    if not isinstance(data, dict):
        raise ValueError("Model cevabi JSON nesnesi olmali.")

    return data


def safe_slug(title: str) -> str:
    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        title.lower(),
    ).strip("-")

    return slug[:70] or "daily-entry"


def generate_entry() -> dict[str, str]:
    # PowerShell tarafından oluşturulan UTF-8 BOM içeren .env
    # dosyalarını da okuyabilmesi için utf-8-sig kullanıyoruz.
    load_dotenv(
        ROOT / ".env",
        encoding="utf-8-sig",
        override=True,
    )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            ".env icinde GEMINI_API_KEY bulunamadi."
        )

    model = os.getenv(
        "GEMINI_MODEL",
        MODEL,
    ).strip()

    day_index = datetime.now().toordinal() % len(TOPICS)
    topic = TOPICS[day_index]

    client = genai.Client(api_key=api_key)

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
- Avoid duplicating trivial examples such as hello world or basic calculators.
- Do not include introductory or concluding text outside the JSON object.

JSON schema:
{{
  "title": "Unique descriptive title",
  "language": "python",
  "description": "One-sentence description",
  "usage": "Brief usage instructions",
  "code": "Complete source code"
}}
"""

    log(f"Gemini istegi gonderiliyor. Model: {model}")

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                response_mime_type="application/json",
            ),
        )
    finally:
        client.close()

    response_text = response.text

    if not response_text:
        raise RuntimeError(
            "Gemini bos cevap dondurdu."
        )

    data = extract_json(response_text)

    required = {
        "title",
        "language",
        "description",
        "usage",
        "code",
    }

    missing = required.difference(data)

    if missing:
        raise ValueError(
            "Eksik model alanlari: "
            + ", ".join(sorted(missing))
        )

    cleaned = {
        key: str(data[key]).strip()
        for key in required
    }

    language = cleaned["language"].lower()

    if language not in ALLOWED_LANGUAGES:
        raise ValueError(
            f"Desteklenmeyen dil: {language}"
        )

    if not cleaned["title"]:
        raise ValueError(
            "Model bos baslik uretti."
        )

    if not cleaned["description"]:
        raise ValueError(
            "Model bos aciklama uretti."
        )

    if not cleaned["code"]:
        raise ValueError(
            "Model bos kod uretti."
        )

    line_count = len(cleaned["code"].splitlines())

    if line_count > 180:
        raise ValueError(
            f"Uretilen kod izin verilen uzunlugu asti: "
            f"{line_count} satir."
        )

    cleaned["language"] = language

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
            "Repoda commit edilmemis degisiklikler var. "
            "Once bunlari commit et veya geri al:\n"
            + "\n".join(relevant_lines)
        )


def create_entry(data: dict[str, str]) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    day_dir = ENTRIES_DIR / today

    if day_dir.exists() and any(day_dir.iterdir()):
        raise RuntimeError(
            f"{today} icin zaten bir kayit olusturulmus."
        )

    day_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    extension = ALLOWED_LANGUAGES[data["language"]]

    code_path = (
        day_dir
        / f"{safe_slug(data['title'])}.{extension}"
    )

    notes_path = day_dir / "README.md"

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
    today = datetime.now().strftime("%Y-%m-%d")

    relative_path = (
        code_path
        .relative_to(ROOT)
        .as_posix()
    )

    row = (
        f"| {today} "
        f"| [{data['title']}]({relative_path}) "
        f"| {data['language'].title()} "
        f"| {data['description']} |\n"
    )

    if README_PATH.exists():
        content = README_PATH.read_text(
            encoding="utf-8"
        )
    else:
        content = ""

    if marker not in content:
        content = f"""# Daily Dev

A collection of small programming utilities and experiments.

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
            "Commit edilecek degisiklik bulunamadi."
        )
        return

    today = datetime.now().strftime("%Y-%m-%d")

    message = (
        f"feat: add {data['title']} ({today})"
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
            "Aktif Git branch'i bulunamadi."
        )

    run_git(
        "push",
        "origin",
        branch,
    )

    log(
        f"GitHub'a gonderildi: {message}"
    )


def main() -> int:
    try:
        ensure_clean_repository()

        entry = generate_entry()

        code_path = create_entry(entry)

        update_readme(
            entry,
            code_path,
        )

        commit_and_push(entry)

        log(
            "Olusturulan dosya: "
            f"{code_path.relative_to(ROOT)}"
        )

        return 0

    except Exception as exc:
        log(f"HATA: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
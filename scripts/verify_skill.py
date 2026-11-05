#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path


REQUIRED_FILES = (
    ".gitattributes",
    ".gitignore",
    ".github/workflows/validate.yml",
    "SKILL.md",
    "AGENTS.md",
    "PITFALLS.md",
    "README.md",
    "LICENSE",
    "NOTICE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CHANGELOG.md",
    "docs/PRODUCT.md",
    "references/report-format.md",
    "agents/openai.yaml",
    "scripts/verify_skill.py",
    "tests/acceptance-cases.md",
    "tests/test_contract.py",
)
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".txt", ".json", ".toml", ".example", ".fixture"}
SPECIAL_TEXT_FILES = {".gitattributes", ".gitignore", "LICENSE", "NOTICE"}
SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}
FORBIDDEN_PATTERNS = (
    re.compile(r"(?i)(?<![\w])[A-Z]:[\\/]"),
    re.compile(r"(?<![\w.])/(?:home|Users)/[A-Za-z0-9._-]+"),
    re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
)
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
TODO_PLACEHOLDER_PATTERN = re.compile(r"(?m)^[ ]{0,3}\[TODO:[^\n]*\][ \t]*$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
CHANGELOG_VERSION_PATTERN = re.compile(r"(?m)^##\s+(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)\s+-\s+\d{4}-\d{2}-\d{2}\s*$")
DOC_VERSION_PATTERN = re.compile(r"(?m)^`(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)`")
SENSITIVE_WINDOWS_PATH = "C:" + "\\Users\\example\\secret"
SENSITIVE_POSIX_PATH = "/" + "home/example/secret"


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def read_text(path: Path, errors: list[str]) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        fail(errors, f"cannot read file: {path}: {exc}")
        return None
    if raw.startswith(b"\xef\xbb\xbf"):
        fail(errors, f"UTF-8 BOM is not allowed: {path}")
        return None
    if b"\r\n" in raw:
        fail(errors, f"CRLF is not allowed: {path}")
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(errors, f"not UTF-8: {path}: {exc}")
        return None


def check_frontmatter(text: str, errors: list[str]) -> str | None:
    if not text.startswith("---\n"):
        fail(errors, "SKILL.md must start with YAML frontmatter")
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        fail(errors, "SKILL.md frontmatter is not closed")
        return None
    frontmatter = text[4:end]
    fields: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    if fields.get("name") != "project-health-lite":
        fail(errors, "SKILL.md name must be project-health-lite")
    if fields.get("license") != "Apache-2.0":
        fail(errors, "SKILL.md license must be Apache-2.0")
    description = fields.get("description", "")
    if len(description) < 30:
        fail(errors, "SKILL.md description is too short")
    if len(description) > 1024:
        fail(errors, "SKILL.md description is too long (maximum 1024)")
    if "<" in description or ">" in description:
        fail(errors, "SKILL.md description cannot contain angle brackets")
    if description.startswith("[TODO:"):
        fail(errors, "SKILL.md description contains an unfinished TODO placeholder")
    metadata_indent: int | None = None
    in_metadata = False
    version_scopes: list[tuple[int, bool]] = []
    for line in frontmatter.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if stripped == "metadata:":
            metadata_indent = indent
            in_metadata = True
            continue
        if metadata_indent is not None and in_metadata and indent <= metadata_indent:
            in_metadata = False
        if stripped.startswith("version:"):
            version_scopes.append((indent, in_metadata))
    if not version_scopes:
        fail(errors, "SKILL.md metadata.version must be present")
        return None
    if any(indent == 0 or not nested for indent, nested in version_scopes):
        fail(errors, "SKILL.md version must be nested under metadata")
        return None
    version = fields.get("version", "")
    if not VERSION_PATTERN.fullmatch(version):
        fail(errors, "SKILL.md metadata.version must be a semantic version")
        return None
    return version


def check_version_consistency(root: Path, version: str, errors: list[str]) -> None:
    changelog = read_text(root / "CHANGELOG.md", errors)
    if changelog is not None:
        match = CHANGELOG_VERSION_PATTERN.search(changelog)
        if not match:
            fail(errors, "CHANGELOG.md must start with a version heading")
        elif match.group(1) != version:
            fail(errors, f"CHANGELOG.md version {match.group(1)} does not match SKILL.md version {version}")

    for relative in ("README.md", "docs/PRODUCT.md"):
        text = read_text(root / relative, errors)
        if text is None:
            continue
        versions = set(DOC_VERSION_PATTERN.findall(text))
        if versions != {version}:
            found = ", ".join(sorted(versions)) or "none"
            fail(errors, f"{relative} version marker must be {version}; found {found}")


def check_openai_yaml(text: str, errors: list[str]) -> None:
    if "interface:" not in text:
        fail(errors, "agents/openai.yaml must contain interface")
    match = re.search(r"short_description:\s*[\"']?(.+?)[\"']?\s*$", text, re.MULTILINE)
    if not match:
        fail(errors, "agents/openai.yaml must contain short_description")
        return
    value = match.group(1).strip()
    if not 25 <= len(value) <= 64:
        fail(errors, f"short_description length must be 25-64: {len(value)}")
    prompt = re.search(r"default_prompt:\s*[\"']?(.+?)[\"']?\s*$", text, re.MULTILINE)
    if not prompt:
        fail(errors, "agents/openai.yaml must contain default_prompt")
    elif "$project-health-lite" not in prompt.group(1):
        fail(errors, "agents/openai.yaml default_prompt must mention $project-health-lite")


def check_links(path: Path, text: str, root: Path, errors: list[str]) -> None:
    for target in LINK_PATTERN.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean = target.split("#", 1)[0]
        if not clean:
            continue
        resolved = (path.parent / clean).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            fail(errors, f"link escapes repository: {path}: {target}")
            continue
        if not resolved.exists():
            fail(errors, f"broken relative link: {path}: {target}")


def iter_text_files(root: Path) -> Iterator[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name not in SKIP_DIRS)
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if path.suffix.lower() in TEXT_SUFFIXES or name in SPECIAL_TEXT_FILES:
                yield path


def check_tree(root: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_FILES:
        if not (root / name).is_file():
            fail(errors, f"missing required file: {name}")
    if errors:
        return errors

    skill = read_text(root / "SKILL.md", errors)
    version: str | None = None
    if skill is not None:
        version = check_frontmatter(skill, errors)
        check_links(root / "SKILL.md", skill, root, errors)
        if version is not None:
            check_version_consistency(root, version, errors)

    openai = read_text(root / "agents" / "openai.yaml", errors)
    if openai is not None:
        check_openai_yaml(openai, errors)

    license_text = read_text(root / "LICENSE", errors)
    if license_text is not None:
        if "Apache License" not in license_text or "Version 2.0" not in license_text:
            fail(errors, "LICENSE must contain Apache License Version 2.0")

    license_path = root / "LICENSE"
    for path in iter_text_files(root):
        if not path.is_file():
            continue
        if path == license_path:
            continue
        text = read_text(path, errors)
        if text is None:
            continue
        if TODO_PLACEHOLDER_PATTERN.search(text):
            fail(errors, f"unfinished TODO: {path.relative_to(root)}")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                fail(errors, f"forbidden sensitive pattern: {path.relative_to(root)}")
        if path.suffix.lower() == ".md":
            check_links(path, text, root, errors)
    return errors


def write_fixture(root: Path) -> None:
    files = {
        "SKILL.md": (
            "---\n"
            "name: project-health-lite\n"
            "description: test description long enough for validation\n"
            "license: Apache-2.0\n"
            "metadata:\n"
            "  version: 1.2.3\n"
            "---\n\n"
            "# Test\n"
        ),
        ".gitattributes": "* text=auto eol=lf\n",
        ".gitignore": "__pycache__/\n",
        ".github/workflows/validate.yml": "name: test\n",
        "AGENTS.md": "# Test\n",
        "PITFALLS.md": "# Test\n",
        "README.md": "# Test\n\n`1.2.3`: test\n",
        "LICENSE": "Apache License\nVersion 2.0\n",
        "NOTICE": "Test\n",
        "CONTRIBUTING.md": "# Test\n",
        "SECURITY.md": "# Test\n",
        "CHANGELOG.md": "## 1.2.3 - 2026-01-01\n\n- Test\n",
        "docs/PRODUCT.md": "# Test\n\n`1.2.3`: test\n",
        "references/report-format.md": "# Test\n",
        "agents/openai.yaml": (
            'interface:\n'
            '  display_name: "Test"\n'
            '  short_description: "A short description long enough"\n'
            '  default_prompt: "Use $project-health-lite to test."\n'
        ),
        "scripts/verify_skill.py": "# Placeholder\n",
        "tests/acceptance-cases.md": "# Test\n",
        "tests/test_contract.py": "# Test\n",
    }
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        write_lf(path, content)


def write_lf(path: Path, content: str) -> None:
    path.write_bytes(content.replace("\r\n", "\n").encode("utf-8"))


def self_test() -> int:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        write_fixture(root)
        if check_tree(root):
            print("self-test failed: valid fixture was rejected")
            return 1

        skill = root / "SKILL.md"
        write_lf(skill, skill.read_text(encoding="utf-8").replace("project-health-lite", "wrong-name", 1))
        if not check_tree(root):
            print("self-test failed: wrong name was accepted")
            return 1

        write_fixture(root)
        skill = root / "SKILL.md"
        write_lf(skill, skill.read_text(encoding="utf-8").replace(
            "metadata:\n  version: 1.2.3", "version: 1.2.3", 1
        ))
        if not check_tree(root):
            print("self-test failed: top-level version was accepted")
            return 1

        write_fixture(root)
        (root / "README.md").write_bytes(b"\xef\xbb\xbf# Test\n\n`1.2.3`: test\n")
        if not check_tree(root):
            print("self-test failed: BOM was accepted")
            return 1

        write_fixture(root)
        write_lf(root / "README.md", f"# Test\n\n`1.2.3`: test\n\n{SENSITIVE_WINDOWS_PATH}\n")
        if not check_tree(root):
            print("self-test failed: local path was accepted")
            return 1

        write_fixture(root)
        write_lf(root / "README.md", f"# Test\n\n`1.2.3`: test\n\n{SENSITIVE_POSIX_PATH}\n")
        if not check_tree(root):
            print("self-test failed: POSIX local path was accepted")
            return 1

        write_fixture(root)
        write_lf(root / "README.md", "# Test\n\n`1.2.3`: test\n\n未完成的 TODO/FIXME 只是说明文字\n")
        if check_tree(root):
            print("self-test failed: TODO prose was rejected")
            return 1

        write_fixture(root)
        write_lf(root / "README.md", "# Test\n\n`1.2.3`: test\n\n[TODO: finish the docs]\n")
        if not check_tree(root):
            print("self-test failed: TODO placeholder was accepted")
            return 1

        write_fixture(root)
        write_lf(root / "README.md", "# Test\n\n`1.2.3`: test\n\n[broken](missing.md)\n")
        if not check_tree(root):
            print("self-test failed: broken link was accepted")
            return 1

        write_fixture(root)
        write_lf(root / "README.md", "# Test\n\n`1.2.3`: test\n\n[escape](../../outside.md)\n")
        if not check_tree(root):
            print("self-test failed: escaping link was accepted")
            return 1

        write_fixture(root)
        write_lf(root / "README.md", "# Test\n\n`1.2.3`: test\n\n" + "ghp_" + "a" * 20 + "\n")
        if not check_tree(root):
            print("self-test failed: GitHub token was accepted")
            return 1

        write_fixture(root)
        write_lf(root / "CHANGELOG.md", "## 9.9.9 - 2026-01-01\n\n- Test\n")
        if not check_tree(root):
            print("self-test failed: version mismatch was accepted")
            return 1

        write_fixture(root)
        write_lf(root / "README.md", "# Test\n\n`9.9.9`: test\n")
        if not check_tree(root):
            print("self-test failed: README version mismatch was accepted")
            return 1

        write_fixture(root)
        (root / "README.md").write_bytes(b"# Test\r\n\r\n`1.2.3`: test\r\n")
        if not check_tree(root):
            print("self-test failed: CRLF was accepted")
            return 1

        write_fixture(root)
        skill = root / "SKILL.md"
        write_lf(skill, skill.read_text(encoding="utf-8").replace("test description long enough for validation", "short", 1))
        if not check_tree(root):
            print("self-test failed: short description was accepted")
            return 1

        write_fixture(root)
        write_lf(root / "LICENSE", "MIT License\n")
        if not check_tree(root):
            print("self-test failed: wrong license was accepted")
            return 1

        write_fixture(root)
        openai = root / "agents" / "openai.yaml"
        write_lf(openai, openai.read_text(encoding="utf-8").replace("$project-health-lite", "$other-skill", 1))
        if not check_tree(root):
            print("self-test failed: default_prompt without skill name was accepted")
            return 1

        write_fixture(root)
        openai = root / "agents" / "openai.yaml"
        write_lf(openai, openai.read_text(encoding="utf-8").replace(
            '  default_prompt: "Use $project-health-lite to test."\n', "", 1
        ))
        if not check_tree(root):
            print("self-test failed: missing default_prompt was accepted")
            return 1

        write_fixture(root)
        (root / ".git").mkdir()
        write_lf(root / ".git" / "README.md", f"{SENSITIVE_WINDOWS_PATH}\n")
        if check_tree(root):
            print("self-test failed: ignored .git directory was scanned")
            return 1

        write_fixture(root)
        write_lf(root / "scripts" / "verify_skill.py", "# Test\n\n" + SENSITIVE_WINDOWS_PATH + "\n")
        if not check_tree(root):
            print("self-test failed: validator itself was not scanned")
            return 1

        write_fixture(root)
        (root / "PITFALLS.md").unlink()
        missing = check_tree(root)
        if not any("missing required file: PITFALLS.md" in error for error in missing):
            print("self-test failed: missing PITFALLS.md was accepted")
            return 1
    print("verify_skill self-test: ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    errors = list(dict.fromkeys(check_tree(args.root.resolve())))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("verify_skill: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())

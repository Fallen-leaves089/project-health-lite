#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path


REQUIRED_FILES = (
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
)
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".txt", ".json", ".toml"}
FORBIDDEN_PATTERNS = (
    re.compile(r"C:\\Users\\"),
    re.compile(r"D:\\codex\\"),
    re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
)
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
TODO_PLACEHOLDER_PATTERN = re.compile(r"(?m)^[ ]{0,3}\[TODO:[^\n]*\][ \t]*$")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def read_text(path: Path, errors: list[str]) -> str | None:
    raw = path.read_bytes()
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


def check_frontmatter(text: str, errors: list[str]) -> None:
    if not text.startswith("---\n"):
        fail(errors, "SKILL.md must start with YAML frontmatter")
        return
    end = text.find("\n---\n", 4)
    if end < 0:
        fail(errors, "SKILL.md frontmatter is not closed")
        return
    frontmatter = text[4:end]
    fields: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    if fields.get("name") != "project-health-lite":
        fail(errors, "SKILL.md name must be project-health-lite")
    description = fields.get("description", "")
    if len(description) < 30:
        fail(errors, "SKILL.md description is too short")
    if description.startswith("[TODO:"):
        fail(errors, "SKILL.md description contains an unfinished TODO placeholder")


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


def check_tree(root: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_FILES:
        if not (root / name).is_file():
            fail(errors, f"missing required file: {name}")
    if errors:
        return errors

    skill = read_text(root / "SKILL.md", errors)
    if skill is not None:
        check_frontmatter(skill, errors)
        check_links(root / "SKILL.md", skill, root, errors)

    openai = read_text(root / "agents" / "openai.yaml", errors)
    if openai is not None:
        check_openai_yaml(openai, errors)

    license_text = read_text(root / "LICENSE", errors)
    if license_text is not None:
        if "Apache License" not in license_text or "Version 2.0" not in license_text:
            fail(errors, "LICENSE must contain Apache License Version 2.0")

    verifier = root / "scripts" / "verify_skill.py"
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path == verifier:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {".gitignore", ".gitattributes"}:
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
        "SKILL.md": "---\nname: project-health-lite\ndescription: test description long enough for validation\n---\n\n# Test\n",
        "AGENTS.md": "# Test\n",
        "PITFALLS.md": "# Test\n",
        "README.md": "# Test\n",
        "LICENSE": "Apache License\nVersion 2.0\n",
        "NOTICE": "Test\n",
        "CONTRIBUTING.md": "# Test\n",
        "SECURITY.md": "# Test\n",
        "CHANGELOG.md": "# Test\n",
        "docs/PRODUCT.md": "# Test\n",
        "references/report-format.md": "# Test\n",
        "agents/openai.yaml": 'interface:\n  display_name: "Test"\n  short_description: "A short description long enough"\n',
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
        (root / "README.md").write_bytes(b"\xef\xbb\xbf# Test\n")
        if not check_tree(root):
            print("self-test failed: BOM was accepted")
            return 1

        write_fixture(root)
        write_lf(root / "README.md", "C:\\Users\\example\\secret\n")
        if not check_tree(root):
            print("self-test failed: local path was accepted")
            return 1

        write_fixture(root)
        write_lf(root / "README.md", "未完成的 TODO/FIXME 只是说明文字\n")
        if check_tree(root):
            print("self-test failed: TODO prose was rejected")
            return 1

        write_fixture(root)
        write_lf(root / "README.md", "[TODO: finish the docs]\n")
        if not check_tree(root):
            print("self-test failed: TODO placeholder was accepted")
            return 1

        write_fixture(root)
        write_lf(root / "README.md", "[broken](missing.md)\n")
        if not check_tree(root):
            print("self-test failed: broken link was accepted")
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

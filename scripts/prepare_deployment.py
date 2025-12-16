"""Prepare project for cloud deployment by removing non-essential files.

Usage:
  python scripts/prepare_deployment.py --dry-run
  python scripts/prepare_deployment.py --apply

Defaults to --dry-run to avoid accidental deletions. The script prints
what would be removed and only deletes with --apply.

It is conservative by default and excludes core app files (app/, core/, requirements.txt,
Dockerfile, docker-compose.yml, etc.).

Files/folders considered for removal (configurable):
- tests/
- docs/ (optionally keep README.md)
- .github/workflows/
- notebooks/ or any .ipynb
- scripts/* (local dev scripts) except this script and run_local scripts if desired
- tests/artifacts/
- temp/ (if present)

Make sure to run git status / push changes before `--apply` so you can recover.
"""
from __future__ import annotations
import argparse
import os
import shutil
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

# Default targets to consider for removal
DEFAULT_TARGETS = [
    "tests",
    "docs",
    ".github/workflows",
    "notebooks",
    "*.ipynb",
    "tests/artifacts",
    "temp",
    "build",
    "dist",
]

# Files and directories to always preserve (safety)
SAFE_PRESERVE = [
    "app",
    "core",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    "DEPLOYMENT.md",
    "README.md",
    "QUICKSTART.md",
    "config.py",
    "scripts/prepare_deployment.py",  # this file
]


def find_candidates(root: Path, patterns: list[str]) -> list[Path]:
    candidates = []
    for p in patterns:
        # handle globs
        for match in root.glob(p):
            candidates.append(match)
    # Also check literal names
    for name in patterns:
        p = root / name
        if p.exists() and p not in candidates:
            candidates.append(p)
    # Deduplicate and sort
    uniq = sorted({c.resolve() for c in candidates})
    return [Path(u) for u in uniq]


def is_safe_to_remove(path: Path) -> bool:
    # Don't remove important files or folders
    for safe in SAFE_PRESERVE:
        safe_path = (ROOT / safe).resolve()
        try:
            if path.resolve() == safe_path or safe_path in path.resolve().parents:
                return False
        except Exception:
            continue
    return True


def print_candidates(candidates: list[Path]):
    if not candidates:
        print("No candidates found for removal.")
        return
    print("Candidates to remove:")
    for c in candidates:
        print(f" - {c.relative_to(ROOT)}")


def remove_paths(candidates: list[Path]):
    removed = []
    for c in candidates:
        try:
            if not is_safe_to_remove(c):
                print(f"Skipping (protected): {c}")
                continue
            if c.is_dir():
                shutil.rmtree(c)
            else:
                c.unlink()
            removed.append(c)
            print(f"Removed: {c}")
        except Exception as e:
            print(f"Failed to remove {c}: {e}")
    return removed


def main():
    parser = argparse.ArgumentParser(description="Prepare project for cloud deployment (safe cleanup).")
    parser.add_argument("--apply", action="store_true", help="Apply deletions (default: dry-run)")
    parser.add_argument("--targets", nargs="*", help="Override default targets (globs or names)")
    parser.add_argument("--keep-docs", action="store_true", help="Keep docs/ directory")
    parser.add_argument("--keep-tests", action="store_true", help="Keep tests/ directory")
    args = parser.parse_args()

    patterns = DEFAULT_TARGETS.copy()
    if args.targets:
        patterns = args.targets

    # Respect keep flags
    if args.keep_docs and "docs" in patterns:
        patterns.remove("docs")
    if args.keep_tests and "tests" in patterns:
        patterns.remove("tests")

    candidates = find_candidates(ROOT, patterns)

    # Filter out anything unsafe
    candidates = [c for c in candidates if is_safe_to_remove(c)]

    if not candidates:
        print("No removable items found (after safety checks).")
        return 0

    print_candidates(candidates)

    if not args.apply:
        print("\nDry-run mode. To actually remove these files, re-run with --apply (use with caution).")
        return 0

    # Confirm
    confirm = input("Type 'YES' to confirm deletion: ")
    if confirm != "YES":
        print("Aborted by user. No files deleted.")
        return 0

    removed = remove_paths(candidates)
    print(f"\nRemoval completed. {len(removed)} items removed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

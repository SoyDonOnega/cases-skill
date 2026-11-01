#!/usr/bin/env python3
"""Freeze or verify a golden cases file.

  python3 scripts/freeze.py freeze <cases-file>   write <cases-file>.sha256 and make both read-only
  python3 scripts/freeze.py verify <cases-file>   exit 1 if the file changed since it was frozen

Standard library only. Refreezing an existing file needs --refreeze, used only after the user approves the change.
"""
import hashlib
import os
import stat
import sys
from pathlib import Path


def fail(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_only(path: Path) -> None:
    os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 2 or args[0] not in ("freeze", "verify"):
        fail("usage: freeze.py freeze|verify <cases-file> [--refreeze]")
    cmd, path = args[0], Path(args[1])
    if not path.is_file():
        fail(f"cases file not found: {path}")
    lock = path.with_name(path.name + ".sha256")

    if cmd == "freeze":
        if lock.exists() and "--refreeze" not in args:
            fail(f"{path} is already frozen; refreeze only after the user approves the change (--refreeze)")
        for p in (path, lock):
            if p.exists():
                os.chmod(p, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        lock.write_text(f"{digest(path)}  {path.name}\n")
        read_only(path)
        read_only(lock)
        print(f"frozen: {path} ({lock.name})")
        return

    if not lock.exists():
        fail(f"{path} is not frozen: no {lock.name}")
    expected = lock.read_text().split()[0]
    if digest(path) != expected:
        fail(f"{path} changed since it was frozen; restore it or ask the user to approve a refreeze")
    print(f"ok: {path} matches {lock.name}")


if __name__ == "__main__":
    main()

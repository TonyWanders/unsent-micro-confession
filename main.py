#!/usr/bin/env python3
"""Write one two-part micro-confession to /output/entry.txt.

Deterministic: no network, no clock, no randomness. The entry is a fixed
string. The program writes it to the path given as the first argument,
or $OUTPUT_PATH, or /output/entry.txt by default, prints it to stdout,
and enforces the competition gate: 1 to 260 characters, not only white
space, exactly two lines, the first a To: line, the second one line of
at most 200 characters, no em dash, no explanation after it.
Pass --check to validate without writing anything.
"""

import os
import sys
from pathlib import Path

ENTRY = (
    "To: my older brother\n"
    "I still have the apology I typed the night you moved out, I just "
    "never sent it because saying sorry felt smaller than the years I "
    "stayed quiet."
)

MIN_CHARS = 1
MAX_CHARS = 260
MAX_MESSAGE_CHARS = 200
DEFAULT_PATH = "/output/entry.txt"

USAGE = (
    "usage: main.py [OUTPUT_PATH] [--check]\n"
    "Write the two-part micro-confession to OUTPUT_PATH, or $OUTPUT_PATH,\n"
    "or /output/entry.txt by default. Use --check to validate without writing.\n"
)


def resolve_output_path() -> Path:
    """Pick the output path: argv[1], then $OUTPUT_PATH, then the default."""
    args = [a for a in sys.argv[1:] if a != "--check"]
    if args:
        return Path(args[0])
    env_path = os.environ.get("OUTPUT_PATH")
    if env_path:
        return Path(env_path)
    return Path(DEFAULT_PATH)


def validate(text: str) -> int:
    """Enforce the competition gate.

    Returns the character count. Raises ValueError when the gate fails.
    """
    chars = len(text)
    if not (MIN_CHARS <= chars <= MAX_CHARS):
        raise ValueError(f"entry is {chars} characters, outside 1-260")
    if not text.strip():
        raise ValueError("entry is only white space")
    if "\u2014" in text:
        raise ValueError("entry contains an em dash")
    lines = text.split("\n")
    if len(lines) != 2:
        raise ValueError(f"entry has {len(lines)} lines, expected 2")
    if not lines[0].startswith("To: ") or not lines[0][4:].strip():
        raise ValueError("first line must be a To: line naming who it was for")
    if not lines[1].strip():
        raise ValueError("entry has an empty message line")
    if len(lines[1]) > MAX_MESSAGE_CHARS:
        raise ValueError(
            f"message line is {len(lines[1])} characters, over 200"
        )
    return chars


def write_entry(path: Path) -> None:
    """Write the fixed entry text to the output path, creating parents."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(ENTRY, encoding="utf-8")


def main() -> int:
    if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
        print(USAGE, end="")
        return 0

    try:
        chars = validate(ENTRY)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    if "--check" in sys.argv[1:]:
        lines = ENTRY.split("\n")
        print(
            f"entry is valid: {chars} characters, "
            f"{len(lines)} lines, "
            f"line 1 {len(lines[0])} chars, line 2 {len(lines[1])} chars"
        )
        return 0

    path = resolve_output_path()
    write_entry(path)
    print(ENTRY)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

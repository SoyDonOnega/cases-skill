# cases

Agent skill `/cases`: golden test cases from a source of truth, approved and frozen before implementation. Part of OneStack.

## What it does

Takes a source of truth (law, spec, documentation, official examples) and a one-sentence description of the unit under test. An isolated subagent that sees only those two inputs proposes cases tagged by origin (`official`, `derived`, `boundary`), each with a citation, and lists what it discarded for lack of a citation and what it could not cover. Ambiguities become `disputed` cases with the competing readings. After your approval the cases are frozen (SHA-256 lock file, read-only) and a minimal adapter turns them into tests in the project's framework: it checks the hash first and skips disputed cases. Implementation runs against the frozen cases; on a failure the skill stops and asks whether the code or the case is wrong. It never computes expected values from the project's code and never edits a frozen case.

## Usage

```text
/cases <source path or text> <unit description> <target folder>
```

Output: a review table (id, input, expected, origin, citation, status) with the discarded and uncovered lists, then a frozen cases file (JSON, YAML or CSV) with its `.sha256` and a test adapter.

## Install

From OneStack: `./sync-install.sh` — or copy this folder as `<skills dir>/cases/`.

## Requirements

Python 3 (standard library) for `scripts/freeze.py`.

## Layout

- `SKILL.md` — the skill.
- `agents/cases-generator.md` — contract for the isolated subagent.
- `scripts/freeze.py` — freeze and verify a cases file.

## License

MIT — see `LICENSE`.

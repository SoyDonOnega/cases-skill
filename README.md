# cases

Agent skill `/cases`: golden test cases from a source of truth, approved and frozen before implementation. Part of OneStack.

## What it does

Takes a source of truth (law, spec, documentation, official examples) and a one-sentence description of the unit under test. An isolated subagent that sees only those two inputs proposes cases tagged by origin (`oficial`, `derivado`, `limite`), each with a citation, and lists what it could not cover. After your approval the cases are frozen (read-only or checksum) and a minimal adapter turns them into tests in the project's framework. Implementation runs against the frozen cases; on a failure the skill stops and asks whether the code or the case is wrong. It never computes expected values from the project's code and never edits a frozen case.

## Usage

```text
/cases <source path or text> <unit description> <target folder>
```

Output: a review table (id, entrada, esperado, origen, cita), then a frozen cases file (JSON, YAML or CSV) and a test adapter.

## Install

From OneStack: `./sync-install.sh` — or copy this folder as `<skills dir>/cases/`.

## Requirements

None.

## Layout

- `SKILL.md` — the skill.

## License

MIT — see `LICENSE`.

---
name: cases
description: >-
  Generates golden test cases with known expected results from an external source of truth
  (law, spec, documentation, official examples) before implementation, in isolation from the
  code, then freezes them and wires them into the project's test framework. Domain-agnostic:
  all domain knowledge comes from the source. Use when the user runs /cases <source> <unit>
  <target folder>.
license: MIT
argument-hint: "<source path or text> <unit description> <target folder>"
disable-model-invocation: true
---

# Cases

Builds test cases whose expected values come from a source of truth, not from the code, so the tests do not inherit the implementation's biases. It does not interpret the source beyond what it states, and it never changes a frozen case.
Paths in this file are relative to the skill root (the folder that contains this SKILL.md).

## Inputs

1. **Source of truth**: path or text. Required. If missing, ask for it and stop.
2. **Unit under test**: one sentence describing the behaviour. Never its code.
3. **Target folder** for the cases.

## When invoked

1. **Scope.** Fix the source and the unit description. Pass nothing else to the subagent.
2. **Generate in isolation.** Spawn an isolated subagent with a fresh context and give it only `agents/cases-generator.md`, the source and the unit description: no code, no conversation history. It returns `cases`, `discarded` and `uncovered`.
3. **Human review.** Show the user, in the user's language:
   - a table of the cases (id, input, expected, origin, citation, status), with `derived` cases flagged as priority to review and `disputed` cases with their competing readings;
   - the `discarded` list (what the subagent tried but could not cite), for information only;
   - the `uncovered` parts of the source.
   Wait for approval. The user may approve, drop or correct cases, or resolve a dispute by choosing a reading. Write no test until the user approves.
4. **Freeze.** Save the approved cases (format below) as JSON, YAML or CSV in the target folder. Run `python3 scripts/freeze.py freeze <file>`: it writes `<file>.sha256` and makes both read-only. Copy `scripts/freeze.py` into the project only if the user wants it there.
5. **Adapter.** Detect the project's test framework from the repo (pytest, vitest, etc.) and write a minimal adapter that:
   - before any test, recomputes the SHA-256 of the cases file and fails the run if it differs from `<file>.sha256`;
   - turns each `approved` case into one test named by its `id`;
   - skips each `disputed` case, with its description as the skip reason.
6. **Implement** against the cases without modifying them.
7. **On a failure:** stop and ask the user whether the error is in the code or in the case. Never edit the case to make it pass. If the user says the case is wrong, or resolves a dispute later, edit only what the user approved and run `freeze.py freeze <file> --refreeze`.

## Case format

| Field | Content |
|---|---|
| `id` | unique identifier |
| `description` | what the case checks; for `derived`, the steps; for `disputed`, the competing readings |
| `input` | input |
| `expected` | expected result (`null` while disputed) |
| `origin` | `official` (verbatim from the source) · `derived` (computed from a cited rule) · `boundary` (edge of a rule) |
| `citation` | exact location in the source |
| `status` | `approved` · `disputed` |

## Rules

- Never compute an expected value by running the project's code.
- No citation from the source, no case.
- Ambiguous source: mark the case `disputed`; do not assume an interpretation.
- The subagent must state which parts of the source it could not cover.
- The implementing agent cannot modify frozen cases; only the user approves a refreeze.

## Example of use

Source: a shipping-fee spec. "Orders under 50.00 pay 4.90. Orders of 50.00 or more ship free. Example: an order of 30.00 pays 4.90."
Unit: "Returns the shipping fee for an order total."

| id | input | expected | origin | citation | status |
|---|---|---|---|---|---|
| C1 | 30.00 | 4.90 | official | §Example | approved |
| C2 | 50.00 | 0.00 | boundary | §Rule 2, "50.00 or more" | approved |
| C3 | 49.99 | 4.90 | boundary | §Rule 1, "under 50.00" | approved |
| C4 | -10.00 | null | boundary | §Rule 1; silent on negative totals | disputed |

Discarded: "orders over 1,000 need a signature" (not in the source). Uncovered: currency, rounding. After approval the cases are frozen to `tests/golden/shipping_fee.json` with `shipping_fee.json.sha256`; a pytest adapter checks the hash, parametrizes C1 to C3 and skips C4.

## Resources

- `agents/cases-generator.md`: contract for the isolated subagent (inputs, task, JSON output, rules).
- `scripts/freeze.py`: `freeze` (hash + read-only) and `verify` a cases file; `--refreeze` only after user approval.

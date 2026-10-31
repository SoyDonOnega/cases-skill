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
2. **Generate in isolation.** Spawn an isolated subagent with a fresh context that sees only the source and the unit description: no code, no conversation history. Instruct it to:
   - produce cases in the format below;
   - tag each case's origin:
     - `oficial`: example taken verbatim from the source;
     - `derivado`: computed step by step from a cited rule;
     - `limite`: boundary of a rule (zero, exact threshold, negative, empty);
     - `sin-fuente`: discard it;
   - mark a case `disputado` when the source is ambiguous, without choosing an interpretation;
   - list the parts of the source it could not cover.
3. **Human review.** Show the user a table (id, entrada, esperado, origen, cita), with `derivado` cases flagged as priority to review, plus the uncovered parts. Wait for approval. Write no test until the user approves.
4. **Freeze.** Save the approved cases as JSON, YAML or CSV in the target folder. Make the file read-only or store a checksum hash next to it.
5. **Adapter.** Detect the project's test framework from the repo (pytest, vitest, etc.) and generate a minimal adapter that turns the frozen cases into tests.
6. **Implement** against the cases without modifying them.
7. **On a failure:** stop and ask the user whether the error is in the code or in the case. Never edit the case to make it pass.

## Case format

| Field | Content |
|---|---|
| `id` | unique identifier |
| `descripcion` | what the case checks |
| `entrada` | input |
| `esperado` | expected result |
| `origen` | `oficial` · `derivado` · `limite` |
| `cita` | exact location in the source |
| `estado` | `aprobado` · `disputado` |

## Rules

- Never compute an expected value by running the project's code.
- No citation from the source, no case.
- Ambiguous source: mark the case `disputado`; do not assume an interpretation.
- The subagent must state which parts of the source it could not cover.
- The implementing agent cannot modify frozen cases.

## Example of use

Source: a shipping-fee spec. "Orders under 50.00 pay 4.90. Orders of 50.00 or more ship free. Example: an order of 30.00 pays 4.90."
Unit: "Returns the shipping fee for an order total."

| id | entrada | esperado | origen | cita | estado |
|---|---|---|---|---|---|
| C1 | 30.00 | 4.90 | oficial | §Example | aprobado |
| C2 | 50.00 | 0.00 | limite | §Rule 2, "50.00 or more" | aprobado |
| C3 | 49.99 | 4.90 | limite | §Rule 1, "under 50.00" | aprobado |
| C4 | -10.00 | ? | limite | §Rule 1; silent on negative totals | disputado |

Uncovered: currency, rounding. After approval the cases are frozen to `tests/golden/shipping_fee.json` with a hash, and a pytest adapter parametrizes one test per case.

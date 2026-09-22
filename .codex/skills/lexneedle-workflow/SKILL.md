---
name: lexneedle-workflow
description: Plan and implement substantial LexNeedle changes in small, verified slices. Use when requirements are ambiguous, a public behavior changes, multiple components are involved, or an implementation needs sequencing.
---

# LexNeedle Development Workflow

Use enough planning to make the next change unambiguous, not enough process to
obscure it. For a clear, small fix, state the contract and implement it. For
public, risky, ambiguous, or multi-component work, use the workflow below.

## Plan only when it adds value

Before implementation, identify the affected public behavior, acceptance
criteria, dependencies, invariants, risks, and verification command. Ask for a
decision when matching semantics, dependencies, serialization, or performance
targets are not defined. Do not create persistent plan files unless the user or
repository workflow asks for them.

## Implement in vertical slices

Choose the smallest end-to-end behavior, test it, implement it, and verify it
before the next slice. Tackle uncertain Unicode alignment or overlap behavior
early. Keep unrelated refactors separate from behavior changes.

Each slice must leave the package usable and reviewable. Prefer a direct
function or dataclass to a framework. Do not expose incomplete public options
without a documented and tested contract.

## Checkpoint

After each meaningful slice, run the focused test. At the final checkpoint run
the relevant Ruff, `ty`, pytest, and build commands. Preserve unrelated changes
and report verification evidence rather than repeating unchanged checks.

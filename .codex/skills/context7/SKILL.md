---
name: context7
description: Use this skill when using the context7 MCP server.
---

# Context7 MCP Server — Usage Rules

Context7 fetches up-to-date, version-specific documentation and code examples for any library or framework. Use it instead of relying on potentially stale training data when you need accurate API references, configuration patterns, or usage examples for external dependencies.

## Core Principle

**Resolve first, then query.** Context7 has a two-step workflow: `resolve-library-id` to find the canonical library ID, then `query-docs` to fetch the actual documentation. Skipping the resolve step wastes a query and risks hitting the wrong library.

## When to Use Context7

Use Context7 whenever the task involves:

- Looking up API references, configuration options, or method signatures for an external library
- Verifying the current syntax or behavior of a framework (training data may be stale)
- Finding real code examples for a specific library version
- Onboarding to a new dependency before writing code that uses it
- Resolving ambiguity between similar packages (e.g., `nextjs` vs `Next.js`)
- Checking version-specific behavior (e.g., breaking changes between major versions)
- Confirming a library's exact name, punctuation, or canonical form before referencing it

**Do NOT use Context7 for:**

- Questions about the user's own codebase (use CodeGraph or Kodit instead)
- General programming concepts with no library-specific context
- Trivial syntax you already know (e.g., basic Python `for` loops, standard `Array.prototype.map`)
- Libraries that aren't indexed — `resolve-library-id` will return no matches
- Sensitive or proprietary information — never include API keys, passwords, credentials, or proprietary code in queries

## Tool Selection Guide

### 1. Resolve the library — `resolve-library-id`

**Always call this first** unless the user explicitly provides a library ID in `/org/project` or `/org/project/version` format. It returns:

- Library ID in Context7-compatible format (e.g., `/vercel/next.js`)
- Name, description, and code snippet count
- Source reputation (High / Medium / Low / Unknown)
- Benchmark score (quality indicator, 100 is highest)
- Available versions

**Key parameters:**

- `query` (required) — natural-language description of what you're trying to accomplish (used to rank results by relevance)
- `libraryName` (required) — official library name with proper punctuation (e.g., `"Next.js"` not `"nextjs"`, `"Customer.io"` not `"customerio"`, `"Three.js"` not `"threejs"`)

**Selection criteria when multiple matches exist:**

1. Name similarity (exact matches prioritized)
2. Description relevance to the query's intent
3. Documentation coverage (higher snippet count = better)
4. Source reputation (High > Medium > Low > Unknown)
5. Benchmark score (higher = better)

**Limit:** Do not call more than 3 times per question. If you cannot find what you need after 3 calls, use the best result you have.

### 2. Query the documentation — `query-docs`

Once you have a library ID, use this to fetch actual documentation. It returns:

- Up-to-date documentation snippets
- Code examples with surrounding context
- Version-specific behavior (when a version is specified in the library ID)

**Key parameters:**

- `libraryId` (required) — Context7-compatible ID from `resolve-library-id` (e.g., `/vercel/next.js` or `/vercel/next.js/v14.3.0-canary.87`)
- `query` (required) — specific question, scoped to ONE concept per call

**Query best practices:**

- Be specific: `"How to set up authentication with JWT in Express.js"` not `"auth"`
- One concept per query: split multi-part questions into separate calls
- Include relevant details: framework version, language, use case
- Don't include sensitive data: no API keys, passwords, credentials, personal data, or proprietary code

**Limit:** Do not call more than 3 times per question.

### 3. Version-specific queries

If the user specifies a version, include it in the library ID:

- `/vercel/next.js/v14.3.0-canary.87` — version-pinned
- `/vercel/next.js` — latest

Use version-pinned queries when:

- The user explicitly mentions a version
- You're debugging version-specific behavior
- Breaking changes between versions matter
- The library has a known unstable API surface

## Efficiency Rules

1. **Always resolve before querying.** Skipping `resolve-library-id` wastes a `query-docs` call and risks the wrong library.
2. **One well-formed query beats five vague ones.** Each MCP call has overhead. Make the query specific enough to return useful results on the first try.
3. **Scope queries to one concept.** Multi-part questions should be split into separate calls — don't combine `"auth and routing and caching"` into one query.
4. **Use the official library name.** `"Next.js"` not `"nextjs"`, `"Customer.io"` not `"customerio"`, `"Three.js"` not `"threejs"`. Punctuation matters for matching.
5. **Don't re-query what you already have.** If `query-docs` returned the answer, use it — don't search again.
6. **Batch independent queries in parallel** when there are no dependencies between them (e.g., resolving multiple libraries at once).
7. **Stop at 3 calls.** The tool has a hard limit per question; if you haven't found it by then, use the best result you have.
8. **Prefer version-pinned queries** when the user specifies a version or you're working with a known version.
9. **Skip resolve when the ID is given.** If the user provides a library ID in `/org/project` or `/org/project/version` format, go straight to `query-docs`.

## Common Workflows

### "How do I use API X in library Y?"

1. `resolve-library-id` with `libraryName: "Y"` and a `query` describing what you want to do
2. `query-docs` with the returned library ID and a specific question about API X
3. If results are off-target, refine the query and retry

### "What's the current syntax for X?"

1. `resolve-library-id` for the library
2. `query-docs` with a specific question about the syntax
3. If the user mentioned a version, pin it in the library ID

### "Find me an example of doing X with library Y"

1. `resolve-library-id` for Y
2. `query-docs` with `"example of X using Y"` or similar
3. The response includes code snippets with context

### "Resolve ambiguity between similar packages"

1. `resolve-library-id` with the ambiguous name
2. Review the multiple matches returned
3. Select based on name similarity, description relevance, snippet count, reputation, and benchmark score

### "User provided a library ID directly"

1. Skip `resolve-library-id`
2. Go straight to `query-docs` with the provided ID

### "Check version-specific behavior"

1. `resolve-library-id` to confirm the library and available versions
2. `query-docs` with the version-pinned library ID (e.g., `/org/project/v1.2.3`)
3. The response reflects that version's documented behavior

## Anti-Patterns

- ❌ Calling `query-docs` without first calling `resolve-library-id` (unless ID is provided)
- ❌ Using vague queries like `"auth"` or `"hooks"` — be specific about what you need
- ❌ Combining multiple concepts in one query — split into separate calls
- ❌ Using informal library names (`"nextjs"` instead of `"Next.js"`) — punctuation matters
- ❌ Calling more than 3 times per question — the tool has a hard limit
- ❌ Including sensitive data in queries (API keys, passwords, credentials, proprietary code)
- ❌ Using Context7 for the user's own codebase (use CodeGraph or Kodit)
- ❌ Re-querying when you already have the answer
- ❌ Skipping version pinning when the user specifies a version

## Quick Reference

```plaintext
resolve-library-id    → find canonical library ID (always call first)
query-docs            → fetch up-to-date docs and code examples
```

**Two-step workflow:** `resolve-library-id` → `query-docs`
**Version pinning:** `/org/project/v1.2.3` for version-specific docs
**Call limit:** 3 calls per question (hard limit)
**Skip resolve when:** user provides a library ID in `/org/project` or `/org/project/version` format

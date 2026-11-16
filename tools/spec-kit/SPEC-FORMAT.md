# Spec Sheet: the spec format

A spec is one Markdown file. `build_spec.py` turns it into one page: a contents rail on the left, a link on every
heading, a table of every work package with status filters, and each package as a strip that opens in place.

    python3 build_spec.py <spec.md> <out.html>

Publish `out.html` as an Artifact. Edit the Markdown, rebuild, publish again to the same link.

## The file

```markdown
---
title: Clearance & Autopilot Build Specification
program: Hangar · Clearance / Autopilot
board: https://claude.ai/artifact/<strip board id>
source: https://claude.ai/artifact/<the document this was converted from, if any>
updated: 2026-11-16
---

Two or three sentences: what this spec builds and for whom. This is the lead.

## How to use this spec {#how-to-use}

Plain sections hold prose, lists, tables and code.

### Roles

A `###` that does not start with a package id is a plain sub-heading.

## Work packages: Clearance {#clearance}

### C-7 · Tool rules dry run
<!-- pkg status=live wave=W5 strip=C-4 depends=C-2,R-3 -->

**Goal.** One sentence.

**Scope.** What is in, what is out.

**Done when.** The checks that prove it, as a list.

**Evidence.** Links to PRs, runs, packets.
```

## Rules

1. **Front matter**: `title` is required. `board` links the program's Strip Board. `source` links the original document.
2. **Sections** are `## Heading`. Add `{#slug}` to pin the link; without it the link is made from the heading text.
   Once a spec is published, pin every section so links never change.
3. **Work packages** are `### ID · Title` where the id looks like `R-1`, `A-9`, `G-ARGO-10`, `INF-2`. The package's
   link is its id in lower case (`#c-7`). Ids never change and are never reused.
4. **The package line** right under the heading is optional: `<!-- pkg status=… wave=… strip=… depends=… -->`.
   - `status`: `done`, `live`, `built`, `verified`, `in-progress`, `review`, `draft`, `proposal`, `not-started`,
     `later`, `unverified`, `blocked`, `owner`, `dropped`, `superseded`.
   - `wave`: the delivery wave (`W3`). `strip`: the Strip Board strip that tracks it. `depends`: ids, comma separated.
5. **Package body**: keep the same four parts in the same order where they apply: Goal, Scope, Done when, Evidence.
   A package that is not started may have only Goal and Scope.
6. **Status lives in the package line**, not in prose, so the table and the filters stay true. The Strip Board holds
   what is happening now; the spec holds what was agreed and whether it is done.
7. **Public pages**: no account ids, bucket names or other real identifiers.

## Files

- `build_spec.py`: the generator (needs `markdown-it-py`).
- `spec-template.html`: the page (Hangar tokens, light and dark).
- `specs/<name>/spec.md`: one folder per spec; `spec.html` is built, never edited by hand.

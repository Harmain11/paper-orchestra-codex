---
name: paper-orchestra-write
description: Audit research evidence and draft LaTeX manuscripts with the active Codex session by default; Google's separate API-based pipeline is optional.
---

# PaperOrchestra manuscript writer

Activate this skill when a user asks to organize evidence, audit a study, or
draft or refine an academic paper from research files, figures, or a LaTeX
template. The default writing engine is the model in this active Codex session.

Read `../../references/RESEARCH_INTEGRITY.md`. Google's PaperOrchestra CLI is
optional and independently installed; it is not embedded. Do not require it
for the normal Codex-native workflow.

## Default workflow: use Codex

1. **Inventory** source files, protocols, numerical tables, and target venue.
   Identify unverified and missing results before generating text.
2. **Audit** source claims manually and numerically where possible. Do not
   infer that an available file is valid merely because it exists.
3. **Prepare** an immutable source snapshot with the local helper when Python
   is available: `python scripts/po_bridge.py prepare --materials PATH
   --bundle PATH`. By default it expects `idea_sparse.md` and
   `experimental_log.md`.
4. **Verify** with `python scripts/po_bridge.py audit --bundle PATH` and
   inspect the SHA-256 manifest. If Python is unavailable, continue with a
   clearly labeled manual review; never claim that the hash audit passed.
   Keep private files out of public Git repositories.
5. **Draft in the active Codex session**: produce a paper outline, methods,
   results, limitations, references from sources the user provides, and LaTeX
   as requested. Use only supported findings. Mark missing evidence and
   uncertain references; never invent data, citations, or conclusions.
6. **Review before writing files**: show the structure and key unsupported
   claims. Save or overwrite files only in the requested project and preserve
   existing work.
7. **Post-process**: check LaTeX compilation when tools are available,
   quantitative claims, source citations, plot provenance, reference links,
   and manuscript consistency. Provide an audit report and unresolved items.

This path uses the model available in the current Codex app/session. It does
not need a separate Gemini, Vertex, or OpenAI API key, and does not invoke the
Google PaperOrchestra Python runner. Codex usage and data handling remain
subject to the user's Codex plan, account settings, and controls.

## Optional Google multi-agent runner

Use this only when the user specifically chooses the upstream Google
PaperOrchestra pipeline. First show a dry-run using `run --upstream PATH
--bundle PATH --output-dir PATH --template-dir PATH`. It requires a separate
upstream checkout and provider credentials, may incur provider charges, and
may transmit research material to that provider. Ask for explicit approval
immediately before using `--execute`. Codex app credentials are not passed to
the separate process.

Never execute with the sample `examples/demo` logs as if they were real
findings. Do not claim any generated text is peer-reviewed.

## Boundaries

No journal submission, Zenodo update, new GPU experiments, author affiliation
claims, or external messages without the user's explicit instruction.

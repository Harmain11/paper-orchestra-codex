---
name: paper-orchestra-write
description: Prepare verifiable evidence and draft a LaTeX research manuscript through Google's PaperOrchestra; uses explicit dry-runs and human-checked science.
---

# PaperOrchestra manuscript writer

Activate this skill when a user asks to draft or refine an academic research
paper using PaperOrchestra, experimental logs, figures, or a LaTeX template.

Read `../../references/RESEARCH_INTEGRITY.md` and the upstream README. The
upstream tool is optional and independently installed; it is not embedded.

## Workflow

1. **Inventory** source files, protocols, numerical tables, and target venue.
   Identify unverified and missing results before generating text.
2. **Audit** source claims manually and numerically where possible. Do not
   infer that an available file is valid merely because it exists.
3. **Prepare** an immutable source snapshot using
   `python scripts/po_bridge.py prepare --materials PATH --bundle PATH`.
   By default it expects `idea_sparse.md` and `experimental_log.md`.
4. **Verify** the snapshot using
   `python scripts/po_bridge.py audit --bundle PATH`. Inspect the SHA-256
   manifest and inputs, and keep private data outside public Git repos.
5. **Draft** a manuscript plan: background, question, design, estimand,
   controls, results, limits, related work, references, and author review.
6. **Dry-run** the launch with `run --upstream PATH --bundle PATH
   --output-dir PATH --template-dir PATH`. `--template-dir` defaults to the
   upstream `templates/cvpr2025`; users can choose a suitable template.
7. Ask for **explicit approval** before API calls. Only after approval use
   the same command with `--execute`; do not claim the output is peer-reviewed.
8. **Post-process**: check LaTeX compilation, quantitative claims, source
   citations, plot provenance, reference links, and manuscript consistency.
   Output an audit report and list all unresolved items.

## Cost and privacy

PaperOrchestra defaults to Gemini model names and may invoke external
LLM APIs. A Codex subscription is not an API credit balance. Do not send raw
materials to external providers without the user's approval. Never execute
with the sample `examples/demo` logs as if they were real findings.

## Boundaries

No journal submission, Zenodo update, new GPU experiments, author affiliation
claims, or external messages without the user's explicit instruction.

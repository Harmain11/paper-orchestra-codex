---
name: paper-orchestra-audit
description: Audit research-paper evidence, file integrity, experimental definitions and citation provenance before using PaperOrchestra or publishing an AI-generated manuscript.
---

# Research evidence audit

Use for manuscript audits, review preparation, and attempts to ground AI-written
papers in actual data. Read `../../references/RESEARCH_INTEGRITY.md`.

1. Identify all supplied raw data, versioned protocols, run manifests, model
   checkpoints, analysis scripts, plots, paper drafts and bibliography files.
2. Use `scripts/po_bridge.py prepare` to create a local evidence snapshot if
   requested. Run `audit --bundle` to detect changes since the snapshot.
3. Distinguish mechanical file integrity from scientific validity. Verify
   reported numeric outcomes against raw records using analysis scripts, when
   available. The tool cannot validate statistics from a filename alone.
4. Check confounds and scope: model size and pinned revision, comparison arms,
   baseline, the measured outcome, sample identities, bootstrap/permutation
   units, tokenization differences, data contamination, null results.
5. Mark every citation `VERIFIED`, `UNVERIFIED`, or `NOT FOUND`, using
   trustworthy original sources, and never fabricate a reference.
6. Produce a concise audit: validated claims, unsupported claims, missing
   controls, recommended corrections, and whether more inference is needed.
7. Keep unpublished or private data local and do not publish anything without
   approval.

Example:

```bash
python scripts/po_bridge.py prepare --materials ./research/raw_materials --bundle ./work/paper1_bundle
python scripts/po_bridge.py audit --bundle ./work/paper1_bundle
```

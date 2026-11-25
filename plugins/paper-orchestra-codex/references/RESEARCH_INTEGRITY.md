# Evidence-first writing requirements

## Invariant rules

1. A claim may enter the paper as a **result** only if it is tied to a named,
   verifiable input (question IDs, raw table, script, protocol, or figure).
2. Distinguish **exploratory**, **pre-registered/confirmatory**, **post hoc**,
   **simulation**, and **hypothetical** analyses. Preserve exact source metrics.
3. Do not merge unrelated populations, benchmarks, edit directions, model
   checkpoints, or scientific estimands just to obtain a more favorable result.
4. No invented citations, DOIs, publications, sample sizes, p-values, figures,
   confidence intervals, implementation details, grant numbers, or results.
5. Keep model outputs separate from human-checked content. Flag missing data
   and label unverified claims as `UNVERIFIED` rather than making assumptions.
6. Human approval is required before adding an author's name, claiming an
   affiliation, changing an already-published paper, or submitting externally.
7. An integrity checksum only shows bytes have not changed since snapshotting;
   it **does not** prove a source result is true or a method is valid.
8. When replacing raw material in a manuscript draft, preserve version history
   and dates. Do not silently rewrite original study provenance.
9. Avoid adding private research materials to a public repository; the plugin
   scaffold and demonstration data must be distinct from user research.
10. Require explicit consent for model calls, downloads, payments, paper
   submissions, or changes to third-party systems.

## Required audit record

Every manuscript run should retain:

- Exact input file names and SHA-256 hashes.
- Dataset identity, model identity/revision, selection rules, exclusion criteria.
- Hypothesis status (pre-specified or exploratory), measured outcome definition,
  baseline and control configuration, sample sizes, uncertainty procedure.
- Plot generation code, available source tabulations, and citation cross-check.
- Limitations and any null/negative results relevant to the claims.
- Output locations, PaperOrchestra Git commit and model-provider settings
  (names only; never API key values), and human review state.

## Literature review

Literature summaries are drafts until the author checks article title, author,
year, venue, DOI/URL, and whether the cited paper actually supports the claim.
Do not invent a reference when retrieval fails. Prefer `citation needed` markers.

## Scientific red flags

- Accuracy vs logit-norm or response-geometry substitution.
- Training, evaluation, and test-set leakage or pretraining exposure.
- Prompt length, token identity, token position, and template confounding.
- A result from one model being described as replication across model families.
- Repeated observations being treated as independent samples.
- Selective reporting of positive effects or excluding failed controls.

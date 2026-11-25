# Contributing

Contributions improving reproducible research authoring, Windows portability,
provenance, documentation, or safe execution are welcome.

1. Open an issue describing the change, expected behavior, and safety impact.
2. Keep the integration thin; upstream features belong in PaperOrchestra.
3. Do not introduce automatic install-time execution, unapproved API calls,
   private datasets, or unverified scientific claims.
4. Run `python -m unittest discover -s tests -v` and
   `python -m compileall -q plugins/paper-orchestra-codex/scripts`.
5. Add a regression test for every new CLI behavior. Update CHANGELOG.md.

All generated manuscript results require human scientific review. Automated
citation matching is not peer review and must never be described as such.

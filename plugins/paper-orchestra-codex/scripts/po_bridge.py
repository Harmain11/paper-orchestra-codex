#!/usr/bin/env python3
"""Safe local bridge for the PaperOrchestra research-writing CLI.

Python 3.11+, standard library only. This project is not an upstream fork.
The wrapper NEVER executes downloads or model calls without --execute.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

UPSTREAM_URL = "https://github.com/google-research/paper-orchestra.git"
PLUGIN_VERSION = "0.2.0"
REQUIRED = ("idea_sparse.md", "experimental_log.md")
EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}
EXCLUDED_FILES = {".env", ".env.local", "id_rsa", "id_ed25519", "secrets.json", "credentials.json"}
EXCLUDED_SUFFIXES = (".pem", ".key", ".p12", ".pfx")


class BridgeError(Exception):
    pass


def resolved(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def contains(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def fingerprint(file: Path) -> str:
    h = hashlib.sha256()
    with file.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def json_write(file: Path, data: dict) -> None:
    file.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def excluded(p: Path) -> bool:
    return p.name.lower() in EXCLUDED_FILES or p.suffix.lower() in EXCLUDED_SUFFIXES or p.name.lower().startswith(".env.")


def assert_source_dir(source: Path) -> None:
    if not source.is_dir():
        raise BridgeError(f"Materials folder does not exist: {source}")
    for name in REQUIRED:
        if not (source / name).is_file():
            raise BridgeError(f"Missing required input: {name} in {source}")


def inspect_source(source: Path, max_file_mb: int) -> tuple[list[tuple[Path, str]], list[str]]:
    """Enumerate regular files only. Never follow symlinks or hide large files."""
    files: list[tuple[Path, str]] = []
    ignored: list[str] = []
    for base, dirs, names in os.walk(source, followlinks=False):
        root = Path(base)
        kept_dirs = []
        for d in sorted(dirs):
            p = root / d
            if p.is_symlink():
                raise BridgeError(f"Refusing symlinked directory: {p.relative_to(source)}")
            if d.lower() in EXCLUDED_DIRS:
                ignored.append(p.relative_to(source).as_posix() + "/")
            else:
                kept_dirs.append(d)
        dirs[:] = kept_dirs
        for name in sorted(names):
            file = root / name
            rel = file.relative_to(source).as_posix()
            if file.is_symlink():
                raise BridgeError(f"Refusing symlinked file: {rel}")
            if excluded(file):
                ignored.append(rel)
                continue
            if not file.is_file():
                raise BridgeError(f"Refusing non-regular input: {rel}")
            if file.stat().st_size > max_file_mb * 1024 * 1024:
                raise BridgeError(f"Input exceeds {max_file_mb} MiB file limit: {rel}")
            files.append((file, rel))
    return files, ignored


def cmd_prepare(args: argparse.Namespace) -> int:
    source, bundle = resolved(args.materials), resolved(args.bundle)
    assert_source_dir(source)
    if source == bundle or contains(source, bundle) or contains(bundle, source):
        raise BridgeError("Source and bundle directories must be separate and non-nested")
    if bundle.exists():
        raise BridgeError(f"Bundle already exists (will not overwrite): {bundle}")
    files, ignored = inspect_source(source, args.max_file_mb)
    bundle.mkdir(parents=True)
    dstroot = bundle / "raw_materials"
    dstroot.mkdir()
    records: list[dict] = []
    for path, rel in files:
        target = dstroot / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        digest = fingerprint(target)
        if digest != fingerprint(path):
            raise BridgeError(f"Checksum mismatch during source copy: {rel}")
        records.append({"path": rel, "sha256": digest, "bytes": target.stat().st_size})
    metadata = {
        "format": "paper-orchestra-codex.evidence-manifest.v1",
        "plugin_version": PLUGIN_VERSION,
        "created_utc": utcnow(),
        "origin_folder_name": source.name,
        "scientific_validity": "NOT ASSESSED; hashes only prove snapshot integrity",
        "files": records,
        "ignored": ignored,
    }
    json_write(bundle / "evidence_manifest.json", metadata)
    print(f"Prepared {len(records)} input files at {bundle}")
    print(f"Excluded common secret/runtime entries: {len(ignored)}")
    print("Scientific validity and citations: NOT VERIFIED")
    return 0


def audit_bundle(bundle: Path) -> tuple[bool, dict]:
    manifest_file = bundle / "evidence_manifest.json"
    material_dir = bundle / "raw_materials"
    if not manifest_file.is_file() or not material_dir.is_dir():
        raise BridgeError("Expected evidence_manifest.json and raw_materials/ in the bundle")
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if manifest.get("format") != "paper-orchestra-codex.evidence-manifest.v1":
        raise BridgeError("Unsupported or missing evidence-manifest format")
    tracked = set()
    failures = []
    for record in manifest.get("files", []):
        rel = record.get("path", "")
        relpath = Path(rel)
        if not rel or relpath.is_absolute() or ".." in relpath.parts or "\\" in rel:
            failures.append(f"unsafe manifest path: {rel}")
            continue
        path = material_dir / relpath
        tracked.add(relpath.as_posix())
        if path.is_symlink() or not path.is_file():
            failures.append(f"missing/non-regular file: {rel}")
        elif fingerprint(path) != record.get("sha256") or path.stat().st_size != record.get("bytes"):
            failures.append(f"changed file: {rel}")
    for p in material_dir.rglob("*"):
        if p.is_symlink():
            failures.append(f"symlink found: {p.relative_to(material_dir).as_posix()}")
        elif p.is_file() and p.relative_to(material_dir).as_posix() not in tracked:
            failures.append(f"untracked file: {p.relative_to(material_dir).as_posix()}")
    ok = not failures and all((material_dir / name).is_file() for name in REQUIRED)
    return ok, {"status": "PASS" if ok else "FAIL", "tracked_files": len(tracked),
                "issues": failures, "scientific_validity": "NOT VERIFIED"}


def cmd_audit(args: argparse.Namespace) -> int:
    ok, result = audit_bundle(resolved(args.bundle))
    print(json.dumps(result, indent=2))
    return 0 if ok else 1


def cmd_doctor(args: argparse.Namespace) -> int:
    data = {
        "python": sys.version.split()[0],
        "python_recommended_3_11_or_newer": sys.version_info >= (3, 11),
        "git_on_path": shutil.which("git") is not None,
        "pdflatex_on_path": shutil.which("pdflatex") is not None,
        "xelatex_on_path": shutil.which("xelatex") is not None,
        "credentials_in_environment_names_only": [k for k in ("OPENAI_API_KEY", "GEMINI_API_KEY", "VERTEX_AI_PROJECT", "VERTEX_AI_LOCATION") if os.environ.get(k)],
        "external_model_calls_on_install": False,
    }
    if args.upstream:
        root = resolved(args.upstream)
        data.update({"upstream_root_exists": root.is_dir(),
                     "upstream_cli_exists": (root / "paper_writing_cli.py").is_file(),
                     "upstream_templates_exist": (root / "templates").is_dir(),
                     "upstream_env_file_present_not_read": (root / ".env").is_file()})
    print(json.dumps(data, indent=2))
    return 0


def cmd_setup(args: argparse.Namespace) -> int:
    target = resolved(args.destination)
    if target.exists():
        raise BridgeError(f"Destination exists; refusing to overwrite: {target}")
    if args.ref and not re.fullmatch(r"[a-zA-Z0-9_.\-/]{1,120}", args.ref):
        raise BridgeError("Invalid ref; use a commit hash or a normal Git tag/branch")
    clone = ["git", "clone", "--depth", "1", UPSTREAM_URL, str(target)]
    print("Plan: " + subprocess.list2cmdline(clone))
    if args.ref:
        print("Requested upstream ref: " + args.ref)
    if not args.execute:
        print("DRY RUN ONLY. Add --execute after reviewing the upstream code and license.")
        return 0
    if shutil.which("git") is None:
        raise BridgeError("git is not installed or not on PATH")
    # A supplied ref may be an old commit, not reachable via shallow clone.
    # Clone normally when pinning to an arbitrary ref.
    if args.ref:
        clone = ["git", "clone", UPSTREAM_URL, str(target)]
    subprocess.run(clone, check=True)
    if args.ref:
        subprocess.run(["git", "checkout", "--detach", args.ref], cwd=target, check=True)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()
    print(f"Upstream cloned at {target} (commit {commit})")
    print("Next: create a Python 3.11 virtual environment, pip install -r requirements.txt, and configure local .env.")
    print("No dependencies installed and no model/API call made by this wrapper.")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    upstream, bundle, output = resolved(args.upstream), resolved(args.bundle), resolved(args.output_dir)
    ok, validation = audit_bundle(bundle)
    if not ok:
        raise BridgeError("Evidence bundle integrity audit failed: " + "; ".join(validation["issues"]))
    material_dir = bundle / "raw_materials"
    if contains(output, material_dir) or contains(material_dir, output) or output == bundle or contains(bundle, output):
        raise BridgeError("Output directory must be separate from the evidence snapshot")
    template = Path(args.template_dir).expanduser()
    if not template.is_absolute():
        template = upstream / template
    template = template.resolve()
    if args.idea_filename not in [p["path"] for p in json.loads((bundle / "evidence_manifest.json").read_text(encoding="utf-8"))["files"]]:
        raise BridgeError(f"Idea file not in snapshot: {args.idea_filename}")
    if args.experimental_log_filename not in [p["path"] for p in json.loads((bundle / "evidence_manifest.json").read_text(encoding="utf-8"))["files"]]:
        raise BridgeError(f"Experiment log not in snapshot: {args.experimental_log_filename}")
    cmd = [sys.executable, str(upstream / "paper_writing_cli.py"),
           "--raw_materials_dir", str(material_dir),
           "--latex_template_dir", str(template),
           "--output_dir", str(output),
           "--idea_filename", args.idea_filename,
           "--experimental_log_filename", args.experimental_log_filename,
           "--use_plotting", str(args.use_plotting).lower(),
           "--writer_model_name", args.writer_model_name,
           "--reflection_model_name", args.reflection_model_name]
    if args.research_cutoff:
        cmd.extend(["--research_cutoff", args.research_cutoff])
    if args.use_plotting:
        cmd.extend(["--plotting_model_name", args.plotting_model_name,
                    "--image_model_name", args.image_model_name])
    print("Planned command:")
    print(subprocess.list2cmdline(cmd))
    print("Warning: upstream may call paid third-party LLM APIs and send your supplied research materials.")
    print("Scientific correctness, bibliographic accuracy, and journal acceptance are NOT guaranteed.")
    if not args.execute:
        print("DRY RUN ONLY. Explicitly add --execute to start upstream PaperOrchestra.")
        return 0
    if not (upstream / "paper_writing_cli.py").is_file() or not template.is_dir():
        raise BridgeError("Missing upstream CLI or LaTeX template directory; run setup and doctor first")
    if output.exists() and any(output.iterdir()):
        raise BridgeError("Output folder is non-empty; refusing to overwrite it")
    output.mkdir(parents=True, exist_ok=True)
    commit = None
    if shutil.which("git") and (upstream / ".git").exists():
        git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=upstream,
                             capture_output=True, text=True, check=False)
        commit = git.stdout.strip() if git.returncode == 0 else None
    json_write(output / "bridge_run_provenance.json", {
        "created_utc": utcnow(), "plugin_version": PLUGIN_VERSION,
        "upstream_git_revision": commit,
        "evidence_manifest_sha256": fingerprint(bundle / "evidence_manifest.json"),
        "model_names_only": {"writer": args.writer_model_name,
                             "reflection": args.reflection_model_name,
                             "plotting": args.plotting_model_name if args.use_plotting else None},
        "scientific_review": "PENDING HUMAN VALIDATION",
        "command": cmd,
    })
    # Do not modify process environment or access upstream .env; upstream owns provider config.
    return subprocess.run(cmd, cwd=upstream, check=False).returncode


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="PaperOrchestra Codex plugin: local evidence-first workflow")
    sub = p.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor", help="Report prerequisites without exposing credential values")
    doctor.add_argument("--upstream", help="Existing PaperOrchestra checkout")
    doctor.set_defaults(func=cmd_doctor)
    setup = sub.add_parser("setup", help="Print or execute an upstream git clone")
    setup.add_argument("--destination", required=True, help="Destination for upstream PaperOrchestra checkout")
    setup.add_argument("--ref", help="Reviewed upstream commit/tag/branch (recommended)")
    setup.add_argument("--execute", action="store_true", help="Actually run git clone; default is dry run")
    setup.set_defaults(func=cmd_setup)
    prepare = sub.add_parser("prepare", help="Copy and SHA-256 fingerprint a research materials snapshot")
    prepare.add_argument("--materials", required=True, help="Input directory with idea_sparse.md and experimental_log.md")
    prepare.add_argument("--bundle", required=True, help="New output bundle directory, outside source")
    prepare.add_argument("--max-file-mb", type=int, default=100, help="Safety limit per input file (default 100 MiB)")
    prepare.set_defaults(func=cmd_prepare)
    audit = sub.add_parser("audit", help="Check a prepared evidence snapshot against recorded hashes")
    audit.add_argument("--bundle", required=True)
    audit.set_defaults(func=cmd_audit)
    run = sub.add_parser("run", help="Preview or start PaperOrchestra using a prepared materials bundle")
    run.add_argument("--upstream", required=True)
    run.add_argument("--bundle", required=True)
    run.add_argument("--output-dir", required=True)
    run.add_argument("--template-dir", default="templates/cvpr2025")
    run.add_argument("--idea-filename", default="idea_sparse.md")
    run.add_argument("--experimental-log-filename", default="experimental_log.md")
    run.add_argument("--writer-model-name", default="gemini-3.1-pro-preview")
    run.add_argument("--reflection-model-name", default="gemini-3.1-pro-preview")
    run.add_argument("--plotting-model-name", default="gemini-3.1-pro-preview")
    run.add_argument("--image-model-name", default="gemini-3-pro-image-preview")
    run.add_argument("--research-cutoff", help="Literature cutoff YYYY-MM")
    run.add_argument("--use-plotting", action="store_true", help="Enable upstream plotting agent")
    run.add_argument("--execute", action="store_true", help="Make upstream model calls; default dry run")
    run.set_defaults(func=cmd_run)
    return p


def main(argv: list[str] | None = None) -> int:
    p = parser()
    args = p.parse_args(argv)
    if getattr(args, "max_file_mb", 1) <= 0:
        p.error("--max-file-mb must be greater than zero")
    try:
        return args.func(args)
    except (BridgeError, OSError, subprocess.CalledProcessError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

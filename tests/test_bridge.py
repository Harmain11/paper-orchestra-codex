"""Offline tests of plugin distribution and local evidence-run safety."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "paper-orchestra-codex"
SCRIPT = PLUGIN / "scripts" / "po_bridge.py"
spec = importlib.util.spec_from_file_location("po_bridge", SCRIPT)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class PluginLayoutTests(unittest.TestCase):
    def test_manifest_and_marketplace(self):
        portable = json.loads((PLUGIN / "plugin.json").read_text(encoding="utf-8"))
        legacy = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        catalog = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(portable["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
        self.assertEqual(portable["name"], legacy["name"])
        self.assertEqual(portable["name"], catalog["plugins"][0]["name"])
        self.assertEqual(portable["version"], legacy["version"])
        self.assertTrue((ROOT / catalog["plugins"][0]["source"]["path"]).is_dir())
        self.assertEqual(catalog["plugins"][0]["source"]["source"], "local")
        self.assertTrue(portable["extensions"]["com.openai"]["requires_local_executor"])
        self.assertTrue((PLUGIN / portable["extensions"]["com.openai"]["onboardingSkill"]).is_file())
        self.assertFalse((PLUGIN / "mcp.json").exists(), "No fake MCP server: skill-only is intentional")

    def test_three_discoverable_skills(self):
        skills = sorted((PLUGIN / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(skills), 3)
        for skill in skills:
            content = skill.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\nname:"))
            self.assertIn("\ndescription:", content)
            self.assertIn("\n---\n", content)
            self.assertLess(len(content), 10000)

    def test_demo_is_clearly_not_science(self):
        text = (ROOT / "examples/demo/raw_materials/experimental_log.md").read_text(encoding="utf-8")
        self.assertIn("NO EXPERIMENTS PERFORMED", text)


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.src = self.base / "materials"
        self.src.mkdir()
        (self.src / "idea_sparse.md").write_text("# question\n", encoding="utf-8")
        (self.src / "experimental_log.md").write_text("# data\n", encoding="utf-8")
        (self.src / "figures").mkdir()
        (self.src / "figures" / "figure.txt").write_text("original", encoding="utf-8")
        self.bundle = self.base / "bundle"

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *args):
        std, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(std), contextlib.redirect_stderr(err):
            result = bridge.main(list(args))
        return result, std.getvalue(), err.getvalue()

    def prepare(self):
        result, out, err = self.cli("prepare", "--materials", str(self.src), "--bundle", str(self.bundle))
        self.assertEqual(result, 0, err + out)
        return json.loads((self.bundle / "evidence_manifest.json").read_text(encoding="utf-8"))

    def test_prepare_and_audit(self):
        m = self.prepare()
        self.assertEqual(len(m["files"]), 3)
        self.assertEqual(m["scientific_validity"], "NOT ASSESSED; hashes only prove snapshot integrity")
        result, out, err = self.cli("audit", "--bundle", str(self.bundle))
        self.assertEqual(result, 0, out + err)
        self.assertIn('"status": "PASS"', out)

    def test_audit_detects_tampering(self):
        self.prepare()
        (self.bundle / "raw_materials" / "experimental_log.md").write_text("changed", encoding="utf-8")
        result, out, _ = self.cli("audit", "--bundle", str(self.bundle))
        self.assertEqual(result, 1)
        self.assertIn("changed file", out)

    def test_audit_detects_added_file(self):
        self.prepare()
        (self.bundle / "raw_materials" / "extra.csv").write_text("x", encoding="utf-8")
        result, out, _ = self.cli("audit", "--bundle", str(self.bundle))
        self.assertEqual(result, 1)
        self.assertIn("untracked file", out)

    def test_prepare_skips_secret_files(self):
        (self.src / ".env").write_text("MY_API_KEY=PRIVATE", encoding="utf-8")
        (self.src / "id_rsa").write_text("PRIVATE", encoding="utf-8")
        m = self.prepare()
        self.assertFalse((self.bundle / "raw_materials" / ".env").exists())
        self.assertEqual(len(m["ignored"]), 2)

    def test_prepare_refuses_existing_bundle(self):
        self.prepare()
        result, _, err = self.cli("prepare", "--materials", str(self.src), "--bundle", str(self.bundle))
        self.assertEqual(result, 2)
        self.assertIn("already exists", err)

    def test_prepare_refuses_nested_output(self):
        result, _, err = self.cli("prepare", "--materials", str(self.src), "--bundle", str(self.src / "new"))
        self.assertEqual(result, 2)
        self.assertIn("non-nested", err)

    def test_prepare_refuses_missing_mandatory_input(self):
        (self.src / "idea_sparse.md").unlink()
        result, _, err = self.cli("prepare", "--materials", str(self.src), "--bundle", str(self.bundle))
        self.assertEqual(result, 2)
        self.assertIn("Missing required", err)

    def test_prepare_refuses_large_files(self):
        (self.src / "large.txt").write_bytes(b"x" * (1024 * 1024 + 1))
        result, _, err = self.cli("prepare", "--materials", str(self.src), "--bundle", str(self.bundle), "--max-file-mb", "1")
        self.assertEqual(result, 2)
        self.assertIn("file limit", err)

    def test_prepare_refuses_symlink(self):
        link = self.src / "linked.txt"
        try:
            link.symlink_to(self.src / "idea_sparse.md")
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks require elevated permissions here")
        result, _, err = self.cli("prepare", "--materials", str(self.src), "--bundle", str(self.bundle))
        self.assertEqual(result, 2)
        self.assertIn("symlinked", err)

    def test_setup_defaults_to_dry_run(self):
        dest = self.base / "upstream"
        result, out, err = self.cli("setup", "--destination", str(dest))
        self.assertEqual(result, 0, err)
        self.assertFalse(dest.exists())
        self.assertIn("DRY RUN ONLY", out)

    def test_run_defaults_to_dry_run_and_keeps_output_absent(self):
        self.prepare()
        target = self.base / "manuscript"
        result, out, err = self.cli("run", "--upstream", str(self.base / "fake-upstream"),
                                    "--bundle", str(self.bundle), "--output-dir", str(target))
        self.assertEqual(result, 0, err)
        self.assertIn("paper_writing_cli.py", out)
        self.assertIn("DRY RUN ONLY", out)
        self.assertFalse(target.exists())

    def test_run_rejects_modified_bundle_even_as_dry_run(self):
        self.prepare()
        (self.bundle / "raw_materials" / "idea_sparse.md").write_text("tampered", encoding="utf-8")
        result, out, err = self.cli("run", "--upstream", str(self.base / "fake-upstream"),
                                    "--bundle", str(self.bundle), "--output-dir", str(self.base / "out"))
        self.assertEqual(result, 2)
        self.assertIn("integrity audit failed", err)

    def test_run_refuses_nonempty_output(self):
        self.prepare()
        upstream = self.base / "fake-upstream"
        (upstream / "templates/cvpr2025").mkdir(parents=True)
        (upstream / "paper_writing_cli.py").write_text("print('fake')", encoding="utf-8")
        out = self.base / "out"
        out.mkdir()
        (out / "keep.txt").write_text("do not erase", encoding="utf-8")
        result, _, err = self.cli("run", "--upstream", str(upstream),
                                  "--bundle", str(self.bundle), "--output-dir", str(out), "--execute")
        self.assertEqual(result, 2)
        self.assertIn("non-empty", err)
        self.assertEqual((out / "keep.txt").read_text(encoding="utf-8"), "do not erase")

    def test_explicit_run_executes_only_local_fake_upstream_and_records_provenance(self):
        self.prepare()
        upstream = self.base / "mock-upstream"
        (upstream / "templates/cvpr2025").mkdir(parents=True)
        # An intentionally tiny, LOCAL fixture with no imports/network/API calls.
        (upstream / "paper_writing_cli.py").write_text(
            "import json, sys, pathlib\n"
            "p = pathlib.Path(sys.argv[sys.argv.index('--output_dir') + 1])\n"
            "(p / 'fake_pipeline_completed.json').write_text(json.dumps({'mock': True}))\n",
            encoding="utf-8")
        out = self.base / "output"
        result, std, err = self.cli("run", "--upstream", str(upstream),
                                    "--bundle", str(self.bundle), "--output-dir", str(out), "--execute")
        self.assertEqual(result, 0, err + std)
        self.assertTrue((out / "fake_pipeline_completed.json").exists())
        provenance = json.loads((out / "bridge_run_provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(provenance["scientific_review"], "PENDING HUMAN VALIDATION")
        self.assertIn("evidence_manifest_sha256", provenance)

    def test_doctor_does_not_show_secrets(self):
        result, out, err = self.cli("doctor")
        self.assertEqual(result, 0, err)
        doc = json.loads(out)
        self.assertFalse(doc["external_model_calls_on_install"])
        self.assertIn("credentials_in_environment_names_only", doc)


if __name__ == "__main__":
    unittest.main()

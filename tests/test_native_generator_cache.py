"""Exact producer cache evidence and the actual workflow's execution ordering."""

import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "release-contract"))
sys.path.insert(0, str(ROOT / "tests"))
import native_generation as generation
import native_generator_cache as cache
import test_native_generation as generation_fixture


FAKE_CARGO = '''#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
import sys
if sys.argv[-1] == '-V':
    print('cargo 1.97.1 (fixture)')
else:
    assert '--locked' in sys.argv and '--release' in sys.argv
    assert sys.argv[sys.argv.index('--features') + 1] == 'release-tooling'
    assert '--no-default-features' not in sys.argv
    assert sys.argv[sys.argv.index('-p') + 1] == 'brokk-bifrost-semantic-packs'
    assert sys.argv[sys.argv.index('--bin') + 1] == 'bifrost-semantic-pack'
    if os.environ.get('FAKE_BUILD_FAIL'):
        raise SystemExit(19)
    target = sys.argv[sys.argv.index('--target') + 1]
    output = Path('target') / target / 'release/bifrost-semantic-pack'
    output.parent.mkdir(parents=True)
    shutil.copy2(os.environ['FAKE_GENERATED_TOOL'], output)
'''


class ProducerCacheTests(unittest.TestCase):
    def setUp(self):
        fixture = generation_fixture.NativeGenerationTests()
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        self.base, self.root = fixture.base, fixture.root
        self.binary, self.config = fixture.write_config(source_build=True)
        for name in cache.RECIPE_PATHS:
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, destination)
        self.workflow = (self.root / cache.RECIPE_PATHS[0]).read_text()
        self.source_archive = self.base / "producer.tar.gz"
        lock = b"fixture locked dependencies\n"
        with tarfile.open(self.source_archive, "w:gz") as archive:
            for name, content in (("Cargo.lock", lock), ("Cargo.toml", b"[workspace]\n")):
                entry = tarfile.TarInfo(f"source/{name}")
                entry.size = len(content)
                archive.addfile(entry, io.BytesIO(content))
        config = json.loads(self.config.read_text())
        config["generator"]["asset_sha256"] = hashlib.sha256(self.source_archive.read_bytes()).hexdigest()
        config["generator"]["build"]["cargo_lock_sha256"] = hashlib.sha256(lock).hexdigest()
        self.config.write_text(json.dumps(config))
        self.tools = self.base / "tools"
        self.tools.mkdir()
        programs = {
            "rustc": "#!/bin/sh\nprintf 'rustc fixture\\nhost: x86_64-unknown-linux-gnu\\nrelease: 1.97.1\\nLLVM version: 99\\n'\n",
            "cargo": FAKE_CARGO,
            "gh": "#!/usr/bin/env python3\nimport os,sys\nfrom pathlib import Path\nsys.stdout.buffer.write(Path(os.environ['FAKE_SOURCE_ARCHIVE']).read_bytes())\n",
        }
        for name, program in programs.items():
            path = self.tools / name
            path.write_text(program)
            path.chmod(0o755)
        self.env = {
            **os.environ, "PATH": str(self.tools) + os.pathsep + os.environ["PATH"],
            "RUNNER_OS": "Linux", "RUNNER_ARCH": "X64", "ImageOS": "ubuntu24",
            "ImageVersion": "fixture-image-1", "CARGO_HOME": str(self.base / "cargo-home"),
            "RUNNER_TEMP": str(self.base / "runner"), "GITHUB_WORKSPACE": str(self.root),
            "GITHUB_REPOSITORY": "BrokkAi/bifrost-packs", "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "1",
            "GITHUB_WORKFLOW_REF": "BrokkAi/bifrost-packs/.github/workflows/native-packs.yml@refs/pull/99/merge",
            "GITHUB_WORKFLOW_SHA": "d" * 40, "FAKE_SOURCE_ARCHIVE": str(self.source_archive),
            "FAKE_GENERATED_TOOL": str(self.binary), "CARGO_BUILD_JOBS": "2",
        }
        # Do not let the caller's optional build flags affect fixture expectations.
        for key in list(self.env):
            if key in cache.BUILD_ENVIRONMENT or key.startswith(("CARGO_PROFILE_", "CARGO_TARGET_")):
                del self.env[key]
        Path(self.env["RUNNER_TEMP"]).mkdir()
        self.commit()
        self.expected_path = self.base / "expected.json"
        self.identity = self.make_identity()
        self.payload = self.base / "payload"
        self.payload.mkdir()
        shutil.copy2(self.binary, self.payload / "bifrost-semantic-pack")
        self.receipt = fixture.write_build_receipt(self.binary, self.config)
        shutil.copy2(self.receipt, self.payload / "build.json")
        self.saved = {}

    def commit(self):
        paths = ["inputs", "native-generation.json", "fake-native-tool", *cache.RECIPE_PATHS]
        subprocess.run(["git", "-C", str(self.root), "add", "--", *paths], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "fixture update"], check=True)

    def make_identity(self):
        identity = cache.build_identity(self.root, self.config, self.env)
        self.expected_path.write_text(json.dumps(identity))
        return identity

    def record(self):
        return cache.record(self.root, self.config, self.payload, self.expected_path, self.env)

    def verify(self):
        return cache.verify(self.root, self.config, self.payload, self.expected_path, self.env)

    def write_manifest(self, value):
        (self.payload / "cache.json").write_text(json.dumps(value))

    def test_exact_hit_accepts_payload_and_preserves_six_field_receipt(self):
        manifest = self.record()
        self.assertEqual(self.verify(), manifest)
        self.assertEqual(set(json.loads((self.payload / "build.json").read_text())), generation.BUILD_RECEIPT_FIELDS)
        self.assertEqual(self.identity["build"], {
            "target": "x86_64-unknown-linux-gnu", "package": "brokk-bifrost-semantic-packs",
            "binary": "bifrost-semantic-pack", "default_features": True,
            "features": ["release-tooling"], "profile": "release", "locked": True,
        })
        expected_digest = hashlib.sha256(json.dumps(self.identity, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(cache.cache_key(self.identity), "native-generator-v2-" + expected_digest)

    def test_changed_identity_dimensions_are_rejected(self):
        original = self.record()
        changes = [
            ("generator", "repository", "different/repository"), ("generator", "commit", "a" * 40),
            ("generator", "asset_sha256", "b" * 64),
            ("toolchain", "rustc", "different rustc"), ("toolchain", "cargo", "different cargo"),
            ("platform", "runner_os", "Windows"), ("platform", "runner_arch", "ARM64"),
            ("platform", "image_version", "other-image"), ("build", "target", "aarch64-unknown-linux-gnu"),
            ("build", "features", []), ("build", "default_features", False),
            ("build", "profile", "dev"), ("environment", "RUSTFLAGS", "-Ctarget-cpu=native"),
            ("recipe", cache.RECIPE_PATHS[0], "c" * 64),
        ]
        for section, field, value in changes:
            with self.subTest(section=section, field=field):
                changed = copy.deepcopy(original)
                changed["identity"][section][field] = value
                self.assertNotEqual(cache.cache_key(changed["identity"]), cache.cache_key(self.identity))
                self.write_manifest(changed)
                with self.assertRaisesRegex(generation.NativeGenerationError, "identity mismatch"):
                    self.verify()
        for field in ("cargo_lock_sha256", "rust_toolchain"):
            changed = copy.deepcopy(original)
            changed["identity"]["generator"]["build"][field] = "changed"
            self.write_manifest(changed)
            with self.assertRaises(generation.NativeGenerationError):
                self.verify()

    def test_current_environment_and_recipe_changes_invalidate_key_and_restore(self):
        self.record()
        for key in ("RUNNER_OS", "RUNNER_ARCH", "ImageOS", "ImageVersion", "RUSTFLAGS",
                    "CARGO_ENCODED_RUSTFLAGS", "CARGO_PROFILE_RELEASE_LTO", "CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_LINKER"):
            with self.subTest(key=key):
                old = self.env.get(key)
                self.env[key] = "changed"
                changed = cache.build_identity(self.root, self.config, self.env)
                self.assertNotEqual(cache.cache_key(changed), cache.cache_key(self.identity))
                with self.assertRaisesRegex(generation.NativeGenerationError, "inputs changed"):
                    self.verify()
                if old is None:
                    del self.env[key]
                else:
                    self.env[key] = old
        for name in cache.RECIPE_PATHS:
            path = self.root / name
            original = path.read_bytes()
            path.write_bytes(original + b"\n")
            with self.subTest(recipe=name), self.assertRaises(generation.NativeGenerationError):
                self.verify()
            path.write_bytes(original)
        cargo_home = Path(self.env["CARGO_HOME"])
        cargo_home.mkdir()
        (cargo_home / "config.toml").write_text('[build]\nrustflags = ["-Copt-level=1"]\n')
        with self.assertRaises(generation.NativeGenerationError):
            self.verify()

    def test_data_only_changes_and_new_run_reuse_original_provenance(self):
        original = self.record()
        config = json.loads(self.config.read_text())
        config["jobs"][0]["name"] = "new-content-plan"
        self.config.write_text(json.dumps(config))
        (self.root / "inputs/artifact.bin").write_bytes(b"new generation input")
        self.env["GITHUB_RUN_ID"] = "456"
        self.commit()
        self.assertEqual(cache.cache_key(cache.build_identity(self.root, self.config, self.env)), cache.cache_key(self.identity))
        self.assertEqual(self.verify()["origin"], original["origin"])
        self.assertNotEqual(generation._source_provenance(self.root)["commit"], original["origin"]["source_commit"])

    def test_actual_source_pins_and_toolchain_bytes_change_key(self):
        self.record()
        original = self.config.read_bytes()
        for field, value in (("repository", "other/repository"), ("commit", "f" * 40),
                             ("asset_sha256", "e" * 64), ("asset", "other-source.tar.gz"),
                             ("cargo_lock_sha256", "d" * 64)):
            config = json.loads(original)
            target = config["generator"]["build"] if field == "cargo_lock_sha256" else config["generator"]
            target[field] = value
            self.config.write_text(json.dumps(config))
            with self.subTest(field=field):
                self.assertNotEqual(cache.cache_key(cache.build_identity(self.root, self.config, self.env)),
                                    cache.cache_key(self.identity))
                with self.assertRaises(generation.NativeGenerationError):
                    self.verify()
        self.config.write_bytes(original)
        rustc = self.tools / "rustc"
        old_rustc = rustc.read_text()
        for before, after in (("LLVM version: 99", "LLVM version: 100"),
                              ("x86_64-unknown-linux-gnu", "aarch64-unknown-linux-gnu")):
            rustc.write_text(old_rustc.replace(before, after))
            self.assertNotEqual(cache.cache_key(cache.build_identity(self.root, self.config, self.env)),
                                cache.cache_key(self.identity))
            with self.assertRaises(generation.NativeGenerationError):
                self.verify()
        rustc.write_text(old_rustc.replace("release: 1.97.1", "release: 1.98.0"))
        with self.assertRaisesRegex(generation.NativeGenerationError, "actual rustc"):
            self.make_identity()

    def test_corrupt_copied_binary_cannot_be_recorded_for_save(self):
        (self.payload / "bifrost-semantic-pack").write_bytes(b"damaged copy")
        with self.assertRaisesRegex(generation.NativeGenerationError, "binary_sha256 mismatch"):
            self.record()
        self.assertFalse((self.payload / "cache.json").exists())

    def test_optional_binary_pin_is_verified_before_recording(self):
        config = json.loads(self.config.read_text())
        config["generator"]["binary_sha256"] = "0" * 64
        self.config.write_text(json.dumps(config))
        self.commit()
        self.make_identity()
        with self.assertRaisesRegex(generation.NativeGenerationError, "configured binary pin"):
            self.record()
        self.assertFalse((self.payload / "cache.json").exists())

    def test_missing_corrupt_symlinked_and_nonexecutable_payloads_fail_closed(self):
        self.record()
        for name in ("bifrost-semantic-pack", "build.json", "cache.json"):
            path = self.payload / name
            original = path.read_bytes()
            with self.subTest(name=name):
                path.unlink()
                with self.assertRaises((OSError, generation.NativeGenerationError)):
                    self.verify()
                target = self.base / "linked-file"
                target.write_bytes(original)
                path.symlink_to(target)
                with self.assertRaises(generation.NativeGenerationError):
                    self.verify()
                path.unlink()
                path.write_bytes(original)
                if name == "bifrost-semantic-pack":
                    path.chmod(0o755)
                path.write_bytes(original + (b"changed" if name == "bifrost-semantic-pack" else b" \n"))
                if name != "cache.json":
                    with self.assertRaises(generation.NativeGenerationError):
                        self.verify()
                path.write_bytes(original)
        binary = self.payload / "bifrost-semantic-pack"
        binary.chmod(0o644)
        with self.assertRaisesRegex(generation.NativeGenerationError, "executable"):
            self.verify()

    def test_malformed_manifest_and_incomplete_origin_are_rejected(self):
        original = self.record()
        for key, value in (("schema_version", True), ("extra", 1), ("identity_sha256", "0" * 64),
                           ("binary_sha256", "0" * 64), ("build_receipt_sha256", "0" * 64), ("origin", {})):
            changed = copy.deepcopy(original)
            changed[key] = value
            self.write_manifest(changed)
            with self.subTest(key=key), self.assertRaises(generation.NativeGenerationError):
                self.verify()
        for key in cache.ORIGIN_FIELDS:
            changed = copy.deepcopy(original)
            changed["origin"][key] = ""
            self.write_manifest(changed)
            with self.subTest(origin=key), self.assertRaises(generation.NativeGenerationError):
                self.verify()
        (self.payload / "cache.json").write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaisesRegex(generation.NativeGenerationError, "duplicate JSON key"):
            self.verify()

    def step(self, marker):
        """Extract one checked-in step's literal shell body; this is not a YAML interpreter."""
        start = self.workflow.rfind("      - ", 0, self.workflow.index(marker) + 1)
        end = self.workflow.find("\n      - ", start + 1)
        return self.workflow[start:end if end != -1 else len(self.workflow)]

    def run_step(self, marker, environment):
        body = self.step(marker).partition("        run: |\n")[2]
        self.assertTrue(body, f"expected literal shell step: {marker}")
        script = textwrap.dedent(body)
        return subprocess.run(["bash", "-e", "-o", "pipefail", "-c", script], cwd=self.root,
                              env=environment, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def attempt(self, number, *, restore="miss", build_fail=False, generation_fail=False):
        runner = self.base / f"attempt-{number}"
        runner.mkdir()
        environment = {**self.env, "RUNNER_TEMP": str(runner), "GITHUB_OUTPUT": str(runner / "outputs"),
                       "GITHUB_ENV": str(runner / "env"), "GITHUB_RUN_ID": str(1000 + number)}
        if build_fail:
            environment["FAKE_BUILD_FAIL"] = "1"
        if generation_fail:
            environment["FAKE_NONDETERMINISTIC"] = "1"
        events = []
        result = self.run_step("id: generator-identity", environment)
        self.assertEqual(result.returncode, 0, result.stdout)
        outputs = dict(line.split("=", 1) for line in Path(environment["GITHUB_OUTPUT"]).read_text().splitlines())
        environment["TARGET_TRIPLE"] = outputs["target"]
        key = outputs["key"]
        payload = runner / "generator-cache"
        if restore != "miss":
            shutil.copytree(self.saved[key], payload)
            if restore == "corrupt":
                (payload / "bifrost-semantic-pack").write_bytes(b"corrupt")
            elif restore == "partial":
                (payload / "stale-extra").write_text("partial key contents")
        built = restore in ("miss", "partial")
        if built:
            events.append("build")
            result = self.run_step("id: generator-build", environment)
            if result.returncode:
                return events, result, key, payload
        events.append("verify")
        result = self.run_step("id: generator-verify", environment)
        if result.returncode:
            return events, result, key, payload
        if built:
            events.append("save")
            saved = self.base / f"saved-{number}"
            shutil.copytree(payload, saved)
            self.saved[key] = saved
        result = self.run_step("name: Select pinned generated tool", environment)
        self.assertEqual(result.returncode, 0, result.stdout)
        environment.update(dict(line.split("=", 1) for line in Path(environment["GITHUB_ENV"]).read_text().splitlines()))
        events.append("generate")
        result = self.run_step("name: Generate twice, verify and compare native content", environment)
        return events, result, key, payload

    def test_workflow_orders_verified_save_before_generation_with_exact_guards(self):
        markers = ["id: generator-identity", "id: generator-cache", "id: generator-build",
                   "id: generator-verify", "id: generator-save", "name: Generate twice, verify and compare native content"]
        positions = [self.workflow.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))
        restore = self.step("id: generator-cache")
        save = self.step("id: generator-save")
        self.assertIn("actions/cache/restore@55cc8345863c7cc4c66a329aec7e433d2d1c52a9", restore)
        self.assertNotIn("restore-keys", restore)
        self.assertIn("key: ${{ steps.generator-identity.outputs.key }}", restore)
        self.assertIn("if: ${{ steps.generator-cache.outputs.cache-hit != 'true' }}", self.step("id: generator-build"))
        self.assertIn("TARGET_TRIPLE: ${{ steps.generator-identity.outputs.target }}", self.step("id: generator-build"))
        self.assertIn("if: ${{ success() && steps.generator-build.outcome == 'success' && steps.generator-verify.outcome == 'success' }}", save)
        self.assertIn("actions/cache/save@55cc8345863c7cc4c66a329aec7e433d2d1c52a9", save)
        self.assertIn("key: ${{ steps.generator-cache.outputs.cache-primary-key }}", save)
        for marker in ("id: generator-verify", "name: Generate twice, verify and compare native content"):
            self.assertNotIn("        if:", self.step(marker))

    def test_successful_build_survives_later_generation_failure_and_exact_restore_still_generates(self):
        events, failed, key, _ = self.attempt(1, generation_fail=True)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("differ", failed.stdout)
        self.assertEqual(events, ["build", "verify", "save", "generate"])
        self.assertIn(key, self.saved)
        origin = json.loads((self.saved[key] / "cache.json").read_text())["origin"]
        (self.root / "inputs/artifact.bin").write_bytes(b"repaired content input")
        self.commit()
        events, passed, restored_key, payload = self.attempt(2, restore="exact")
        self.assertEqual(passed.returncode, 0, passed.stdout)
        self.assertEqual(events, ["verify", "generate"])
        self.assertEqual(restored_key, key)
        self.assertEqual(json.loads((payload / "cache.json").read_text())["origin"], origin)
        receipt = json.loads((payload.parent / "native/generation.json").read_text())
        self.assertEqual(receipt["source"]["commit"], generation._source_provenance(self.root)["commit"])
        self.assertEqual(len(receipt["reproducibility"]["runs"]), 2)
        self.assertEqual(receipt["qualification"]["status"], "pending")

    def test_failed_build_never_verifies_saves_or_generates(self):
        events, result, _, _ = self.attempt(1, build_fail=True)
        self.assertEqual(result.returncode, 19, result.stdout)
        self.assertEqual(events, ["build"])
        self.assertEqual(self.saved, {})

    def test_corrupt_exact_restore_fails_closed_and_partial_hit_rebuilds(self):
        _, first, _, _ = self.attempt(1)
        self.assertEqual(first.returncode, 0, first.stdout)
        events, corrupt, _, _ = self.attempt(2, restore="corrupt")
        self.assertNotEqual(corrupt.returncode, 0)
        self.assertEqual(events, ["verify"])
        events, rebuilt, _, payload = self.attempt(3, restore="partial")
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stdout)
        self.assertEqual(events, ["build", "verify", "save", "generate"])
        self.assertFalse((payload / "stale-extra").exists())


if __name__ == "__main__":
    unittest.main()

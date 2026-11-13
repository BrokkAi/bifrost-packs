"""Stage the Ruby fixture workspaces for the Bifrost 0.15.2 CVE rules.

Each case directory is its own workspace: a Gemfile, a Gemfile.lock for the
case's version (or none), and copies of the reviewed models and policies.
Source files are written by hand and kept; this script only (re)writes the
generated lock files and copies.
Run from the repository root: python3 research/osv-dataflow-2026-11/ruby-0152/generator/mkfx.py
"""

import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[4]
FIXTURES = ROOT / "fixtures/policy/bifrost.security"
POLICIES = ROOT / "rules/bifrost.security/policies/ruby"
WEB = ROOT / "semantic-packs/web-network/ruby/bifrost.web-network-ruby.json"
RUBY = ROOT / "semantic-packs/ruby"

REXML = (["network-xml-to-rexml-attribute-value-dos.rqlp", "network-xml-to-rexml-repeated-declaration-dos.rqlp"], ["bifrost.ruby.rexml.json"])
IMAP = (["network-input-to-net-imap-raw-arguments.rqlp"], ["bifrost.ruby.net-imap.json"])
GEM = (["network-input-to-gem-installer.rqlp"], ["bifrost.ruby.rubygems-installer.json"])

# fixture/case -> (policies and models, gem, locked version or None)
CASES = {
    "ruby-network-xml-to-rexml/rexml-3.2.6": (REXML, "rexml", "3.2.6"),
    "ruby-network-xml-to-rexml/rexml-3.4.1": (REXML, "rexml", "3.4.1"),
    "ruby-network-xml-to-rexml/rexml-3.4.2": (REXML, "rexml", "3.4.2"),
    "ruby-network-xml-to-rexml/incomplete/unlocked": (REXML, "rexml", None),
    "ruby-network-xml-to-rexml/incomplete/helper": (REXML, "rexml", "3.2.6"),
    "ruby-network-input-to-net-imap/net-imap-0.5.14": (IMAP, "net-imap", "0.5.14"),
    "ruby-network-input-to-net-imap/net-imap-0.6.3": (IMAP, "net-imap", "0.6.3"),
    "ruby-network-input-to-net-imap/net-imap-0.5.15": (IMAP, "net-imap", "0.5.15"),
    "ruby-network-input-to-net-imap/incomplete/unlocked": (IMAP, "net-imap", None),
    "ruby-network-input-to-net-imap/incomplete/keywords": (IMAP, "net-imap", "0.5.14"),
    "ruby-network-input-to-net-imap/incomplete/net-imap-0.6.4.1": (IMAP, "net-imap", "0.6.4.1"),
    "ruby-network-input-to-gem-installer/install": (GEM, None, None),
    "ruby-network-input-to-gem-installer/incomplete/helper": (GEM, None, None),
    "ruby-network-input-to-gem-installer/incomplete/lookalike": (GEM, None, None),
}

LOCK = """GEM
  remote: https://rubygems.org/
  specs:
    {gem} ({version})

PLATFORMS
  ruby

DEPENDENCIES
  {gem}

BUNDLED WITH
   2.5.22
"""


def main():
    for case, ((policies, models), gem, version) in CASES.items():
        root = FIXTURES / case
        shutil.rmtree(root / ".bifrost", ignore_errors=True)
        (root / ".bifrost/policies").mkdir(parents=True)
        (root / ".bifrost/semantic-models").mkdir()
        for policy in policies:
            shutil.copy(POLICIES / policy, root / ".bifrost/policies" / policy)
        for model in [WEB, *(RUBY / m for m in models)]:
            shutil.copy(model, root / ".bifrost/semantic-models" / model.name)
        for stale in ("Gemfile", "Gemfile.lock"):
            (root / stale).unlink(missing_ok=True)
        if gem:
            (root / "Gemfile").write_text(f'source "https://rubygems.org"\n\ngem "{gem}"\n')
        if version:
            (root / "Gemfile.lock").write_text(LOCK.format(gem=gem, version=version))


if __name__ == "__main__":
    main()

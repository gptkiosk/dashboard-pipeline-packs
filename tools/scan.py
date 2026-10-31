#!/usr/bin/env python3
"""Scan every pack for injection points: text that could steer an agent instead of describing the project.

Everything in a pack reaches a model as prompt text, so every string is scanned: JSON keys and values, and every
Markdown line. A finding fails the check. Rules live in security/rules.json, each with known-bad samples in
security/fixtures.json. Besides the pattern rules:

- hidden-chars: invisible or direction-changing characters (zero-width, bidi controls, tag characters).
- links: a URL whose host is not one of the pack's service hosts or a platform service host.
- weakened-gates (with --base-ref): a template that drops or downgrades a blocking check, removes a "not an agent
  step" rule or removes a human sign-off compared with the base branch.

security/allow.json lets a maintainer accept a named rule for one pack, with a reason. A pack cannot allow itself:
that file, the rules and this script are owned by the maintainers (see .github/CODEOWNERS).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL_RE = re.compile(r"https?://([A-Za-z0-9.-]+)", re.I)
HIDDEN = re.compile("[­͏؜ᅟᅠ឴឵᠎​-‏‪-‮⁠-⁯ㅤ︀-️﻿ﾠ\U000e0000-\U000e007f]")


def load_rules(path: Path = ROOT / "security" / "rules.json") -> list[tuple[str, re.Pattern]]:
    data = json.loads(path.read_text("utf-8"))
    if (data.get("format"), data.get("version")) != ("dashboard-pack-scan", "1.0"):
        raise SystemExit("security/rules.json is not a dashboard-pack-scan 1.0 file")
    return [(r["id"], re.compile(r["pattern"], re.M)) for r in data["rules"]]


def scan_text(text: str, rules: list[tuple[str, re.Pattern]], hosts: set[str]) -> list[tuple[str, str]]:
    """(rule, matched text) for one string."""
    found = []
    for rule, pattern in rules:
        m = pattern.search(text)
        if m:
            found.append((rule, m.group(0)))
    m = HIDDEN.search(text)
    if m or any(unicodedata.category(ch) == "Cf" for ch in text):
        found.append(("hidden-chars", repr(m.group(0) if m else next(ch for ch in text if unicodedata.category(ch) == "Cf"))))
    for host in URL_RE.findall(text):
        host = host.lower().rstrip(".")
        if not any(host == h or host.endswith("." + h) for h in hosts):
            found.append(("links", host))
    return found


def _strings(value, path=""):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from _strings(item, f"{path}[{i}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield f"{path}.{key}" if path else key, str(key)
            yield from _strings(item, f"{path}.{key}" if path else key)


def scan_pack(folder: Path, rules, platform_hosts: set[str]) -> list[str]:
    try:
        manifest = json.loads((folder / "pack.json").read_text("utf-8"))
    except (OSError, ValueError, UnicodeError):
        return [f"{folder.name}/pack.json: not readable JSON"]
    hosts = set(platform_hosts) | {h.lower() for h in ((manifest.get("service") or {}).get("hosts") or []) if isinstance(h, str)}
    return scan_pack_files(folder, folder.name, rules, hosts)


def scan_pack_files(folder: Path, label: str, rules, hosts: set[str]) -> list[str]:
    encoded = next(p for r, p in rules if r == "encoded")
    findings = []
    for path in sorted(p for p in folder.rglob("*") if p.is_file()):
        rel = f"{label}/{path.relative_to(folder).as_posix()}"
        raw = path.read_text("utf-8", errors="replace")
        if path.suffix == ".json":
            try:
                data = json.loads(raw)
            except ValueError:
                findings.append(f"{rel}: not valid JSON")
                continue
            for where, text in _strings(data):
                findings += [f"{rel}: {where}: {rule}: {hit[:80]!r}" for rule, hit in scan_text(text, rules, hosts)]
            m = encoded.search(raw)             # escapes such as ​ are decoded above; flag that they were used at all
            if m and re.search(r"\\[ux]", m.group(0)):
                findings.append(f"{rel}: encoded: {m.group(0)[:80]!r}")
        else:
            for n, line in enumerate(raw.splitlines(), 1):
                findings += [f"{rel}:{n}: {rule}: {hit[:80]!r}" for rule, hit in scan_text(line, rules, hosts)]
    return findings


def _base_type(ref: str, rel: str) -> dict | None:
    try:
        out = subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=ROOT, capture_output=True, text=True, check=True, timeout=20).stdout
        return json.loads(out)
    except (subprocess.SubprocessError, OSError, ValueError):
        return None


def weakened(before: dict, after: dict) -> list[str]:
    """What a change to a template removes from its safety net."""
    out = []
    now = {c.get("id"): c for c in after.get("checks", []) if isinstance(c, dict)}
    for c in before.get("checks", []):
        if not isinstance(c, dict):
            continue
        new = now.get(c.get("id"))
        if c.get("severity") == "block" and (new is None or new.get("severity") != "block"):
            out.append(f"blocking check {c.get('id')!r} was removed or downgraded")
        elif c.get("kind") == "not_agent_for" and new is None:
            out.append(f"rule {c.get('id')!r} (not an agent step) was removed")
        elif new is not None and c.get("kind") == new.get("kind") == "not_agent_for" and c.get("match") != new.get("match"):
            out.append(f"rule {c.get('id')!r} (not an agent step) now matches something else")
    gone = set(before.get("human_signoffs", [])) - set(after.get("human_signoffs", []))
    if len(after.get("human_signoffs", [])) < len(before.get("human_signoffs", [])):
        out.append(f"human sign-offs went from {len(before['human_signoffs'])} to {len(after.get('human_signoffs', []))}: removed {sorted(gone)}")
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--packs", type=Path, default=ROOT / "packs")
    parser.add_argument("--base-ref", help="git ref to compare templates with, for example origin/main")
    args = parser.parse_args(argv)
    rules = load_rules()
    platform = json.loads((ROOT / "platform" / "tools.json").read_text("utf-8"))
    platform_hosts = {h.lower() for s in platform.get("services", []) for h in s.get("hosts", [])}
    allow = json.loads((ROOT / "security" / "allow.json").read_text("utf-8")).get("allow", {})
    failed = False
    for folder in sorted(p for p in args.packs.iterdir() if p.is_dir() and not p.name.startswith(".")):
        findings = scan_pack(folder, rules, platform_hosts)
        examples = ROOT / "examples" / folder.name           # examples reach a model during rehearsal, so they are scanned too
        if examples.is_dir():
            findings += [f.replace(f"{folder.name}/", f"examples/{folder.name}/", 1) for f in scan_pack_files(examples, folder.name, rules, platform_hosts)]
        if args.base_ref:
            for path in sorted((folder / "project-types").glob("*.json")):
                rel = path.relative_to(ROOT).as_posix()
                before = _base_type(args.base_ref, rel)
                try:
                    after = json.loads(path.read_text("utf-8"))
                except ValueError:
                    continue
                if before:
                    findings += [f"{rel}: weakened-gates: {w}" for w in weakened(before, after)]
        accepted = allow.get(folder.name, {})
        kept = [f for f in findings if not any(f": {rule}:" in f for rule in accepted)]
        if kept:
            failed = True
            print(f"{folder.name}: FAILED", *(f"  - {f}" for f in kept), sep="\n", file=sys.stderr)
        else:
            print(f"{folder.name}: no injection findings" + (f" (accepted: {', '.join(sorted(accepted))})" if accepted else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

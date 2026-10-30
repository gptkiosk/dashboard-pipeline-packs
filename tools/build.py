#!/usr/bin/env python3
"""Validate every pack under packs/ and build the release files into dist/.

dist/ gets one reproducible archive per pack (<id>-<pack_version>.tar.gz), the index pipeline-packs.json that lists each
archive with its sha256, and SHA256SUMS. The release workflow then signs the index; the dashboard trusts nothing else.

The checks here are the structural rules the dashboard enforces at install (apps/api/pipeline_packs.py). With
--dashboard <checkout>, every pack is also run through that dashboard's own validate(), which knows its project-type
schema, shipped guides, checks and connectors.

platform/tools.json lists what a template may require (agents, system tools, providers, checks, services). Every name a
pack or template names must be listed there, and the tool's app_min must not be newer than the pack's. Adding a tool is
its own pull request.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORMAT = ("dashboard-pipeline-pack", "0.1")
INDEX_FORMAT = ("dashboard-pipeline-pack-index", "0.1")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
VERSION_RE = re.compile(r"^\d{1,4}\.\d{1,4}\.\d{1,4}$")
TYPE_RE = re.compile(r"^project-types/[a-z0-9][a-z0-9-]{0,39}\.json$")
GUIDE_RE = re.compile(r"^guides/[a-z0-9][a-z0-9-]{0,60}\.md$")
MAX_FILE_BYTES = 40_000
MAX_FILES = 40
MAX_ARCHIVE_BYTES = 1_000_000
REQUIRE_KINDS = ("agents", "system_tools", "providers", "checks", "services")
AUTHOR_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")


def version_key(value: str) -> tuple[int, ...]:
    return tuple(int(x) for x in value.split("."))


def load_platform(path: Path = ROOT / "platform" / "tools.json") -> dict:
    data = json.loads(path.read_text("utf-8"))
    if (data.get("format"), data.get("version")) != ("dashboard-platform", "1.0"):
        raise SystemExit("platform/tools.json is not a dashboard-platform 1.0 file")
    for kind in REQUIRE_KINDS:
        for tool in data[kind]:
            if not (ID_RE.fullmatch(tool["id"]) or re.fullmatch(r"^[a-z0-9][a-z0-9._-]{0,39}$", tool["id"])) or not tool.get("name") \
                    or not tool.get("description") or not VERSION_RE.fullmatch(tool.get("app_min", "")):
                raise SystemExit(f"platform/tools.json: {kind} entry {tool.get('id')!r} needs id, name, description and app_min")
    return data


def requirements(manifest: dict, files: dict[str, bytes]) -> dict[str, list[str]]:
    """Everything the pack and its templates say they need, merged by kind."""
    need = {k: [] for k in REQUIRE_KINDS}
    need["checks"] += manifest.get("checks") or []
    if (manifest.get("service") or {}).get("id"):
        need["services"].append(manifest["service"]["id"])
    for t in manifest.get("project_types") or []:
        try:
            r = json.loads(files.get(f"project-types/{t}.json", b"{}")).get("requires") or {}
        except (ValueError, UnicodeError):
            continue
        for kind in REQUIRE_KINDS:
            need[kind] += r.get(kind, []) if isinstance(r.get(kind), list) else []
    return {k: sorted(set(v)) for k, v in need.items() if v}


def platform_problems(manifest: dict, files: dict[str, bytes], platform: dict) -> list[str]:
    problems = []
    if not AUTHOR_RE.fullmatch(str(manifest.get("author", ""))):
        problems.append("pack.json needs author: the GitHub account that maintains the pack")
    for kind, names in requirements(manifest, files).items():
        known = {t["id"]: t for t in platform[kind]}
        for name in names:
            if name not in known:
                problems.append(f"requires {kind} {name!r}, which is not in platform/tools.json; adding a tool is its own pull request")
            elif VERSION_RE.fullmatch(str(manifest.get("app_min", ""))) and version_key(known[name]["app_min"]) > version_key(manifest["app_min"]):
                problems.append(f"{kind} {name!r} needs dashboard {known[name]['app_min']}, newer than the pack's app_min {manifest['app_min']}")
    return problems


def settings_labels(manifest: dict, files: dict[str, bytes]) -> list[str]:
    labels = []
    for t in manifest.get("project_types") or []:
        try:
            labels += [f["label"] for f in json.loads(files[f"project-types/{t}.json"]).get("customize", [])]
        except (KeyError, ValueError, UnicodeError, TypeError):
            continue
    return labels


def pack_files(folder: Path) -> tuple[dict[str, bytes], list[str]]:
    files, problems = {}, []
    for path in sorted(folder.rglob("*")):
        rel = path.relative_to(folder).as_posix()
        if path.is_symlink():
            problems.append(f"{rel} is a link; packs hold regular files only.")
        elif path.is_file():
            files[rel] = path.read_bytes()
    return files, problems


def check(folder: Path, files: dict[str, bytes]) -> tuple[dict, list[str]]:
    problems = []
    if len(files) > MAX_FILES:
        problems.append(f"more than {MAX_FILES} files")
    for rel, data in files.items():
        if rel != "pack.json" and not TYPE_RE.fullmatch(rel) and not GUIDE_RE.fullmatch(rel):
            problems.append(f"{rel} is not pack.json, project-types/<id>.json or guides/<name>.md")
        if len(data) > MAX_FILE_BYTES:
            problems.append(f"{rel} is larger than {MAX_FILE_BYTES // 1000} KB")
        try:
            text = data.decode("utf-8")
            if rel.endswith(".json"):
                json.loads(text)
        except (UnicodeError, ValueError):
            problems.append(f"{rel} is not valid UTF-8 {'JSON' if rel.endswith('.json') else 'text'}")
    try:
        m = json.loads(files["pack.json"])
    except (KeyError, ValueError, UnicodeError):
        return {}, problems + ["no readable pack.json"]
    if (m.get("format"), m.get("version")) != FORMAT:
        problems.append("pack.json is not a dashboard-pipeline-pack 0.1 manifest")
    if m.get("id") != folder.name or not ID_RE.fullmatch(str(m.get("id", ""))):
        problems.append(f"pack.json id must be the folder name ({folder.name})")
    for key in ("pack_version", "app_min"):
        if not VERSION_RE.fullmatch(str(m.get(key, ""))):
            problems.append(f"{key} must look like 1.2.3")
    if not str(m.get("label", "")).strip():
        problems.append("the pack needs a label")
    types, guides = m.get("project_types") or [], m.get("guides") or []
    if not types:
        problems.append("the pack must provide at least one project type")
    listed = {f"project-types/{t}.json" for t in types} | {f"guides/{g}" for g in guides} | {"pack.json"}
    for rel in sorted(listed - set(files)):
        problems.append(f"{rel} is listed in pack.json but missing")
    for rel in sorted(set(files) - listed):
        problems.append(f"{rel} is not listed in pack.json")
    for t in types:
        try:
            if json.loads(files.get(f"project-types/{t}.json", b"{}")).get("id") != t:
                problems.append(f"project-types/{t}.json must have id {t!r}")
        except (ValueError, UnicodeError, AttributeError):
            pass
    return m, problems


def dashboard_check(checkout: Path, files: dict[str, bytes]) -> list[str]:
    sys.path.insert(0, str(checkout / "apps" / "api"))
    import pipeline_packs  # noqa: PLC0415 - the checkout is only known at run time
    from version import __version__  # noqa: PLC0415
    return pipeline_packs.validate(files, __version__)[1]


def archive(pack_id: str, files: dict[str, bytes]) -> bytes:
    """A byte-for-byte reproducible tar.gz: sorted names under one top folder, fixed owner, mode and times."""
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        for rel in sorted(files):
            info = tarfile.TarInfo(f"{pack_id}/{rel}")
            info.size, info.mode, info.mtime, info.uid, info.gid, info.uname, info.gname = len(files[rel]), 0o644, 0, 0, 0, "", ""
            tar.addfile(info, io.BytesIO(files[rel]))
    out = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0, compresslevel=9) as gz:
        gz.write(raw.getvalue())
    return out.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--packs", type=Path, default=ROOT / "packs")
    parser.add_argument("--out", type=Path, default=ROOT / "dist")
    parser.add_argument("--dashboard", type=Path, help="a dashboard checkout whose pipeline_packs.validate() every pack must also pass")
    parser.add_argument("--check-only", action="store_true", help="validate, write nothing")
    args = parser.parse_args()

    folders = sorted(p for p in args.packs.iterdir() if p.is_dir() and not p.name.startswith(".")) if args.packs.is_dir() else []
    platform = load_platform()
    failed, entries, archives = False, [], {}
    for folder in folders:
        files, problems = pack_files(folder)
        manifest, more = check(folder, files)
        problems += more
        if manifest:
            problems += platform_problems(manifest, files, platform)
        if not problems and args.dashboard:
            problems += dashboard_check(args.dashboard, files)
        if problems:
            failed = True
            print(f"{folder.name}: FAILED", *(f"  - {p}" for p in problems), sep="\n", file=sys.stderr)
            continue
        name = f"{manifest['id']}-{manifest['pack_version']}.tar.gz"
        data = archive(manifest["id"], files)
        if len(data) > MAX_ARCHIVE_BYTES:
            failed = True
            print(f"{folder.name}: FAILED\n  - the archive is larger than {MAX_ARCHIVE_BYTES // 1000} KB", file=sys.stderr)
            continue
        archives[name] = data
        entries.append({"id": manifest["id"], "pack_version": manifest["pack_version"], "label": manifest["label"],
                        "summary": manifest.get("summary", ""), "service": manifest.get("service"),
                        "archive": name, "sha256": hashlib.sha256(data).hexdigest(), "app_min": manifest["app_min"],
                        "author": manifest["author"], "trust": "official" if manifest["author"] in platform["maintainers"] else "community",
                        "requires": requirements(manifest, files), "settings": settings_labels(manifest, files)})
        print(f"{folder.name}: ok ({manifest['pack_version']}, {len(files)} files)")
    if failed:
        return 1
    if not entries:
        print("No packs under packs/ yet; nothing to release.")
        return 0
    if args.check_only:
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    for stale in args.out.iterdir():
        if stale.is_file():
            stale.unlink()
    for name, data in archives.items():
        (args.out / name).write_bytes(data)
    tools = {kind: [{k: t[k] for k in ("id", "name", "description", "app_min")} for t in platform[kind]] for kind in REQUIRE_KINDS}
    index = {"format": INDEX_FORMAT[0], "version": INDEX_FORMAT[1], "packs": entries, "tools": tools}
    (args.out / "pipeline-packs.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", "utf-8")
    sums = [f"{hashlib.sha256((args.out / n).read_bytes()).hexdigest()}  {n}" for n in sorted([*archives, "pipeline-packs.json"])]
    (args.out / "SHA256SUMS").write_text("\n".join(sums) + "\n", "utf-8")
    print(f"Wrote {len(entries)} pack(s) and the index to {args.out}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

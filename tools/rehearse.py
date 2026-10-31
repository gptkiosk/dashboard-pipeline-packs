#!/usr/bin/env python3
"""Gate 4, rehearsal: plan each template example several times with the dashboard's own planner prompt and check every plan.

For every example of the chosen packs, the dashboard checkout builds the planner prompt (`apps/api/rehearsal.py prompt`, with
the pack installed into a fresh temporary data folder), a model answers it --runs times, and the dashboard judges each answer
(`rehearsal.py judge`): it must parse, pass the dashboard's plan validation, have no blocking plan-check finding, and meet the
example's expectations. A template passes when every run passes. Warnings are reported, not failures.

The dashboard runs without the model key; only this script talks to the model. Prints a Markdown summary and exits 1 on any
failed run.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MAX_CALLS = 40
PLAN_TOKENS = 16_000


def dashboard(checkout: Path, python: str, data: Path, *args: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "OPENROUTER_API_KEY"} | {"MAC_CONTROL_DATA_DIR": str(data)}
    return subprocess.run([python, "rehearsal.py", *args], cwd=checkout / "apps" / "api", env=env, capture_output=True, text=True, timeout=180)


def rehearse(pack: Path, example: Path, checkout: Path, python: str, model_id: str, runs: int) -> list[dict]:
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        built = dashboard(checkout, python, Path(tmp) / "data", "--pack", str(pack), "prompt", str(example))
        if built.returncode != 0:
            detail = (json.loads(built.stdout).get("problems") if built.stdout.startswith("{") else None) or [built.stderr.strip()[-400:]]
            return [{"run": 0, "ok": False, "problems": detail, "stories": 0, "warnings": []}]
        for n in range(1, runs + 1):
            try:
                answer = model.ask(model_id, built.stdout, PLAN_TOKENS)
            except model.ModelError as exc:
                results.append({"run": n, "ok": False, "problems": [str(exc)], "stories": 0, "warnings": []})
                continue
            path = Path(tmp) / f"answer-{n}.txt"
            path.write_text(answer, "utf-8")
            judged = dashboard(checkout, python, Path(tmp) / "data", "--pack", str(pack), "judge", str(example), str(path))
            try:
                verdict = json.loads(judged.stdout)
            except ValueError:
                verdict = {"ok": False, "problems": [judged.stderr.strip()[-400:] or "the judge printed nothing"], "stories": 0, "findings": []}
            results.append({"run": n, "ok": bool(verdict.get("ok")), "problems": verdict.get("problems", []), "stories": verdict.get("stories", 0),
                            "warnings": sorted({f["id"] for f in verdict.get("findings", []) if f.get("severity") != "block"})})
    return results


def summary(rows: list[tuple[str, str, list[dict]]], model_id: str, runs: int) -> str:
    out = [f"### Rehearsal ({model_id}, {runs} run{'s' if runs != 1 else ''} per example)", "",
           "| Template | Example | Passed | Stories | Problems |", "|---|---|---|---|---|"]
    for pack, example, results in rows:
        passed = sum(r["ok"] for r in results)
        problems = "; ".join(sorted({p for r in results for p in r["problems"]}))[:600].replace("|", "\\|").replace("\n", " ")
        stories = ", ".join(str(r["stories"]) for r in results)
        out.append(f"| `{pack}` | {example} | {passed}/{len(results)} | {stories} | {problems or 'none'} |")
    warnings = sorted({w for _, _, results in rows for r in results for w in r["warnings"]})
    if warnings:
        out += ["", "Plan-check warnings seen (not failures): " + ", ".join(f"`{w}`" for w in warnings) + "."]
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dashboard", type=Path, required=True, help="a dashboard checkout that has apps/api/rehearsal.py")
    parser.add_argument("--python", default=sys.executable, help="the Python that has the dashboard's API requirements")
    parser.add_argument("--packs-dir", type=Path, default=ROOT / "packs")
    parser.add_argument("--examples-dir", type=Path, default=ROOT / "examples")
    parser.add_argument("--pack", action="append", default=[], help="pack id to rehearse (repeatable); default: every pack")
    parser.add_argument("--model", default=os.environ.get("REHEARSAL_MODEL", ""))
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args(argv)
    if not (args.dashboard / "apps" / "api" / "rehearsal.py").is_file():
        print("This dashboard has no rehearsal.py yet; rehearsal needs a dashboard with template format 1.0.", file=sys.stderr)
        return 2
    packs = args.pack or sorted(p.name for p in args.packs_dir.iterdir() if p.is_dir() and not p.name.startswith("."))
    plan = [(pack, example) for pack in packs for example in sorted((args.examples_dir / pack).glob("*.json"))]
    if not plan:
        print("No examples to rehearse.", file=sys.stderr)
        return 2
    if len(plan) * args.runs > MAX_CALLS:
        print(f"{len(plan)} examples × {args.runs} runs is more than {MAX_CALLS} model calls; rehearse fewer packs at a time.", file=sys.stderr)
        return 2
    rows = [(pack, example.stem, rehearse(args.packs_dir / pack, example, args.dashboard, args.python, args.model, args.runs)) for pack, example in plan]
    print(summary(rows, args.model, args.runs))
    return 0 if all(r["ok"] for _, _, results in rows for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

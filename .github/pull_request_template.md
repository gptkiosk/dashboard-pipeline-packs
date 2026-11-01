## What this changes

<!-- One or two sentences: the template, what it produces and who it is for. -->

## How I tested it

<!-- Imported into my dashboard with Import a template; what the plans for my examples looked like. -->

## Checklist

- [ ] One pack per pull request, `pack_version` raised and `changes` says what is new in this version.
- [ ] `author` in pack.json is my GitHub account.
- [ ] Only tools listed in `platform/tools.json` are required. (A new tool is a separate pull request.)
- [ ] No checks, sign-offs or "not an agent step" rules were removed or weakened.
- [ ] Settings use closed choices where they can; free-text settings are for facts only.
- [ ] `python3 -m unittest discover -s tests`, `python3 tools/build.py`, `python3 tools/scan.py --base-ref origin/main` and
      `python3 tools/readme.py --check` pass locally.
- [ ] Every borrowed passage in a guide is my own writing or credited with an allowed open licence.

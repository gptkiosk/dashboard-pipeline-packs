#!/usr/bin/env python3
"""Print one Markdown line per pack in a built index, for the draft release notes."""
import json
import sys

for p in json.load(open(sys.argv[1], encoding="utf-8"))["packs"]:
    print("- {} ({} {}, needs dashboard {})".format(p["label"], p["id"], p["pack_version"], p["app_min"]))

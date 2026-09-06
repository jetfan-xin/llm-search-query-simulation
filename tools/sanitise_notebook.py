#!/usr/bin/env python3
"""Create a review-safe notebook copy without changing its code cells.

Added in 2026. Outputs and execution counters may contain local or record-level
material, so they are removed. Historical Windows paths in code cells are made
relative to ``thesis_code``; no other source text is rewritten.
"""

import argparse
import json
from pathlib import Path


ARCHIVED_DRIVE = "D:"
ARCHIVED_ROOT_PARTS = ("RUC", "grad", "code", "mycode")
PRIVATE_ROOTS = (ARCHIVED_DRIVE + "\\" + "\\".join(ARCHIVED_ROOT_PARTS),)


def sanitise(source, destination):
    notebook = json.loads(source.read_text())
    for cell in notebook.get("cells", []):
        cell["execution_count"] = None
        cell["outputs"] = []
        if cell.get("cell_type") != "code":
            continue
        rewritten = []
        for line in cell.get("source", []):
            for private_root in PRIVATE_ROOTS:
                if private_root in line:
                    line = line.replace(private_root, ".").replace("\\", "/")
                    while "//" in line:
                        line = line.replace("//", "/")
            rewritten.append(line)
        cell["source"] = rewritten
    notebook.get("metadata", {}).pop("vscode", None)
    destination.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    sanitise(args.source, args.destination)


if __name__ == "__main__":
    main()

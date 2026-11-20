#!/usr/bin/env python3
"""Standalone Muse runner for the nougentalk persona resolver.

Native Muse packaging of src/nougentalk/persona.py: no pip install, no
NouGenShards dependency. This script puts the repo's own src/ on sys.path
(relative to the repo root) and drives the library exactly the way the
library's own CLI (python -m nougentalk.persona) does:

    Signals.from_texts(texts, surfaces=..., tz=..., role=...,
                       audience_size=..., stable_days=...)
    p = resolve(sig, registry)
    p.system_prompt()   # the addressing contract
    p.fingerprint()     # proof of determinism / cache key

Differences from the library CLI, by design:
- Default output is JSON (the library prints JSON only with --json), and the
  JSON adds "system_prompt" next to "fingerprint" so a lane gets the whole
  contract in one call.
- No --scope mode: shard-backed signal building stays in the library. A lane
  passes observed texts directly.

--check mirrors the library CLI exactly: it lints a draft file against the
resolved persona's contract, prints one "VIOLATION ..." line per violation,
then "# check PASS|FAIL (n violation(s)) against persona <fingerprint>",
and exits 1 on any violation, 0 otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC_CANDIDATES = [
    REPO_ROOT / "src",                                            # inside the repo (muse/ under root)
    Path.home() / "workspace" / "repos" / "nougentalk" / "src",   # installed copy in custom-skills/
]
for _src in _SRC_CANDIDATES:
    if (_src / "nougentalk" / "persona.py").exists():
        sys.path.insert(0, str(_src))
        break
else:  # pragma: no cover - import below will fail loudly with the real error
    sys.path.insert(0, str(_SRC_CANDIDATES[0]))

from nougentalk.persona import Signals, check_output, resolve  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Resolve a deterministic persona contract from observed signals (nougentalk, Muse native)."
    )
    ap.add_argument("--text", action="append", default=[], help="a message from the member (repeatable)")
    ap.add_argument("--file", help="newline-delimited messages")
    ap.add_argument("--surface", action="append", default=[], help="surface the member reads on (repeatable)")
    ap.add_argument("--tz", default="UTC")
    ap.add_argument("--role", default="")
    ap.add_argument("--size", type=int, default=1, help="audience size for the segment test")
    ap.add_argument("--stable-days", type=int, default=0)
    ap.add_argument("--registry", type=Path, help="registry JSON overriding the default markets/audiences")
    ap.add_argument("--check", type=Path,
                    help="draft output file to lint against the resolved persona's contract; exit 1 on violations")
    a = ap.parse_args(argv)

    texts = list(a.text)
    if a.file:
        texts += Path(a.file).read_text(encoding="utf-8").splitlines()
    sig = Signals.from_texts(texts, surfaces=a.surface, tz=a.tz, role=a.role,
                             audience_size=a.size, stable_days=a.stable_days)
    p = resolve(sig, a.registry)

    if a.check:
        viol = check_output(a.check.read_text(encoding="utf-8"), p)
        for x in viol:
            print("VIOLATION " + x)
        print(f"# check {'FAIL' if viol else 'PASS'} ({len(viol)} violation(s)) against persona {p.fingerprint()}")
        return 1 if viol else 0

    print(json.dumps(asdict(p) | {"fingerprint": p.fingerprint(), "system_prompt": p.system_prompt()},
                     indent=1, default=list))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

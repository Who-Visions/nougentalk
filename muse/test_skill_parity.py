"""Parity tests: the Muse runner (muse/resolve.py) must resolve the SAME
persona as the library (src/nougentalk/persona.py) for the same signals.

For every signal set below, the runner is executed as a subprocess (the way a
Muse lane actually calls it) and its JSON fingerprint and system_prompt are
compared against resolve() called in-process. Deterministic, no network.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNER = REPO_ROOT / "muse" / "resolve.py"
sys.path.insert(0, str(REPO_ROOT / "src"))

from nougentalk.persona import Signals, check_output, resolve  # noqa: E402

SIGNAL_SETS: list[dict] = [
    {  # fleet operator: orders, fleet lexicon, eastern tz
        "texts": ["Ship the relay leg and shard the result", "Fix the lane probe, do not ask me twice"],
        "surfaces": ["claude-app"], "tz": "America/New_York", "role": "owner",
    },
    {  # Haitian Creole + immigration/family signals -> contracted audience
        "texts": ["Mwen bezwen renouvle rezidans mwen epi voye papye yo bay avoka a",
                  "Manman mwen ap tann rezilta biometrics li, fanmi a bezwen konnen kisa pou fe"],
        "surfaces": ["whatsapp"], "tz": "America/New_York", "role": "member",
    },
    {  # stream creator
        "texts": ["The twitch overlay broke mid stream and chat could not see the clip",
                  "Check the vod after the stream, viewers are asking for the clip"],
        "surfaces": ["twitch"], "tz": "UTC", "role": "",
    },
    {  # canon keeper
        "texts": ["The protagonist arc in this chapter changes the whole universe",
                  "Write the lore for the film scene and keep the character canon locked"],
        "surfaces": ["chatgpt-app"], "tz": "America/Chicago", "role": "member",
    },
    {  # local GPU builder
        "texts": ["Ollama will not load the gguf, vram is full and the quant is wrong",
                  "Run the e2b build in lm studio and check cuda before you ship it"],
        "surfaces": ["terminal", "github"], "tz": "UTC", "role": "",
    },
    {  # homeowner / business surface
        "texts": ["I need an invoice for the client and the revenue report for the llc",
                  "Tell the customer the price up front and when we will come out"],
        "surfaces": ["phone"], "tz": "America/New_York", "role": "client",
    },
]


def _library_persona(case: dict):
    sig = Signals.from_texts(case["texts"], surfaces=case["surfaces"], tz=case["tz"], role=case["role"])
    return resolve(sig)


def _runner_persona(case: dict) -> dict:
    cmd = [sys.executable, str(RUNNER)]
    for t in case["texts"]:
        cmd += ["--text", t]
    for s in case["surfaces"]:
        cmd += ["--surface", s]
    cmd += ["--tz", case["tz"]]
    if case["role"]:
        cmd += ["--role", case["role"]]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=REPO_ROOT)
    return json.loads(out.stdout)


def test_runner_matches_library_fingerprint_and_prompt():
    assert len(SIGNAL_SETS) >= 5
    for case in SIGNAL_SETS:
        lib = _library_persona(case)
        got = _runner_persona(case)
        assert got["fingerprint"] == lib.fingerprint(), case
        assert got["system_prompt"] == lib.system_prompt(), case
        assert got["audience"] == lib.audience, case
        assert got["market"] == lib.market, case


def test_runner_check_mode_matches_library(tmp_path: Path):
    case = SIGNAL_SETS[1]  # contracted audience (no-id-numbers etc.)
    lib = _library_persona(case)
    bad = tmp_path / "bad.txt"
    bad.write_text("Bonjou, men nimewo a: 123-45-6789 pou dosye a.\n", encoding="utf-8")
    good = tmp_path / "good.txt"
    good.write_text("Bonjou.\nPapye a pare.\n", encoding="utf-8")

    base = [sys.executable, str(RUNNER)]
    for t in case["texts"]:
        base += ["--text", t]
    for s in case["surfaces"]:
        base += ["--surface", s]
    base += ["--tz", case["tz"], "--role", case["role"]]

    lib_bad = check_output(bad.read_text(encoding="utf-8"), lib)
    assert lib_bad, "fixture must violate the library contract"
    r_bad = subprocess.run(base + ["--check", str(bad)], capture_output=True, text=True, cwd=REPO_ROOT)
    assert r_bad.returncode == 1
    assert r_bad.stdout.count("VIOLATION ") == len(lib_bad)
    assert lib.fingerprint() in r_bad.stdout

    lib_good = check_output(good.read_text(encoding="utf-8"), lib)
    assert lib_good == [], "fixture must pass the library contract"
    r_good = subprocess.run(base + ["--check", str(good)], capture_output=True, text=True, cwd=REPO_ROOT)
    assert r_good.returncode == 0
    assert "PASS" in r_good.stdout


if __name__ == "__main__":
    import tempfile

    test_runner_matches_library_fingerprint_and_prompt()
    with tempfile.TemporaryDirectory() as d:
        test_runner_check_mode_matches_library(Path(d))
    print("parity OK")

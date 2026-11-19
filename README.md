<!-- nougen-readme-compiler: v1 -->

# 💬 nougentalk

Deterministic persona/audience resolver: signals in, an addressing contract out.

## 📚 Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Architecture](#architecture)
- [Fleet Role](#fleet-role)
- [License](#license)

## 🧠 Overview

Deterministic, data-driven persona resolver for the NouGen fleet.

Signals in, an addressing contract out: the same `Signals` produce the same `Persona` and the same fingerprint. No model, no randomness, no clock reads inside `resolve()`.

Markets and audiences are generic, data-loadable archetypes (`registry.json`, override-able) — never owner-specific values baked into code.

Extracted from [Who-Visions/NouGenShards](https://github.com/Who-Visions/NouGenShards) `src/nougen_shards/persona.py`, 2026-09-16.

## 🚀 Quick Start

[guess] Install command inferred from pyproject.toml — verify.

```sh
pip install -e .
```

Requires Python 3.10+.

## 🧭 Usage

```python
sig = Signals.from_texts(texts, surfaces=["claude-app"], tz="America/New_York")
p   = resolve(sig)
p.system_prompt()   # style contract for any lane addressing this member
p.fingerprint()     # proof of determinism / cache key
```

## CLI

```sh
python -m nougentalk.persona --text "..." --surface twitch --tz America/New_York --role streamer --json
python -m nougentalk.persona --text "..." --check output.txt   # lint against the resolved contract
```

## 🏗️ Architecture

`Signals` → `resolve()` → `Persona`.

- `Persona.system_prompt()` — the style contract for any lane addressing this member.
- `Persona.fingerprint()` — proof of determinism / cache key.

Markets and audiences are generic, data-loadable archetypes in `registry.json` (override-able); no owner-specific values are baked into code.

## 📌 Fleet Role

Generated from the NouGenRelay fleet manifest — edit the manifest, not this block.

| | |
|---|---|
| Role | persona / audience resolver |
| Kind | satellite |
| Status | canonical |
| Canonical for | persona-resolver |
| Visibility | public |

## 📄 License

MIT, per `pyproject.toml`. No `LICENSE` file was found in the repository.

## 🔗 Links

- [NouGenShards (source of the extraction)](<https://github.com/Who-Visions/NouGenShards>)
- [nougentalk on GitHub](<https://github.com/Who-Visions/nougentalk>)

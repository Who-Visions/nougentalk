# nougentalk

Deterministic, data-driven persona resolver for the NouGen fleet.

```
sig = Signals.from_texts(texts, surfaces=["claude-app"], tz="America/New_York")
p   = resolve(sig)
p.system_prompt()   # style contract for any lane addressing this member
p.fingerprint()     # proof of determinism / cache key
```

Same `Signals` -> same `Persona` -> same fingerprint. No model, no randomness,
no clock reads inside `resolve()`. Markets and audiences are generic,
data-loadable archetypes (`registry.json`, override-able) -- never
owner-specific values baked into code.

Extracted from [Who-Visions/NouGenShards](https://github.com/Who-Visions/NouGenShards)
`src/nougen_shards/persona.py`, 2026-09-16.

## CLI

```
python -m nougentalk.persona --text "..." --surface twitch --tz America/New_York --role streamer --json
python -m nougentalk.persona --text "..." --check output.txt   # lint against the resolved contract
```

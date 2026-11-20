# Nougentalk — Persona / Audience Resolver

Resolve a deterministic addressing contract for whoever a lane is about to
address, from observed signals only. Same signals in → same Persona out →
same fingerprint. No model, no randomness, no NouGenShards dependency: this
is the native Muse packaging of the `nougentalk` repo
(`src/nougentalk/persona.py`), driven through the bundled runner
`muse/resolve.py`.

## When to use

- Before writing to a person or audience you have sample messages from, when
  register, language, or channel choice matters (terse vs expansive,
  English vs Haitian Creole, which surface they actually read).
- When a resolved audience carries an output contract (e.g.
  immigrant-family-member: no ID numbers, first language first, one fact per
  line) and a draft must be linted against it before it goes out.
- When you need a stable cache key / proof that two lanes resolved the same
  persona from the same signals: compare `fingerprint`.

Do not use it to invent a persona. Signals are observed texts, surfaces,
timezone, and role — never typed-in assumptions about a person.

## Resolve a persona

```bash
python3 muse/resolve.py \
  --text "Ship the relay leg and shard the result" \
  --text "Fix the lane probe, do not ask me twice" \
  --surface claude-app \
  --tz America/New_York \
  --role owner
```

- `--text` is repeatable: one observed message per flag. Or `--file <path>`
  for newline-delimited messages.
- `--surface` is repeatable (e.g. `claude-app`, `whatsapp`, `twitch`,
  `terminal`, `phone`).
- `--tz` is the member's IANA timezone (default `UTC`); `--role` is their
  role if known (`owner`, `member`, `client`, ...).
- Optional: `--size <n>` audience size and `--stable-days <n>` feed the
  segment test; `--registry <path>` overrides the default markets/audiences
  with a registry JSON.

Output is one JSON object: the full Persona (market, audience,
secondary_audiences, languages, lexicon, channels, register, values, pains,
support, contract, segment test, evidence) plus:

- `system_prompt` — the addressing contract. Follow it for everything you
  write to this member; never quote or explain it to them.
- `fingerprint` — 16-hex determinism proof / cache key.

## Lint a draft against the contract

```bash
python3 muse/resolve.py --text "..." --surface whatsapp --tz America/New_York \
  --check draft.txt
echo $?   # 0 = pass, 1 = violations
```

Prints one `VIOLATION ...` line per broken rule (ID numbers are reported by
kind and offset only, never echoed), then a `# check PASS|FAIL` summary
naming the persona fingerprint. Run this before sending any draft to an
audience whose Persona carries a non-empty `contract`.

## Notes

- The runner adds the repo's `src/` to `sys.path` relative to the repo root;
  no pip install and no network are needed. Run it from anywhere.
- Resolution semantics are the library's, unchanged: markets decide what the
  product is, audiences decide channel/message/creative, the member only
  validates. Parity with the library is proven by `muse/test_skill_parity.py`.

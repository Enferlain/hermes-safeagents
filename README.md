# hermes-safeagents

Hermes desktop plugin for local SafeAgents-powered security observation, private
review, and offline decision-model replay. Log-only by design: the plugin never
changes enforcement, never executes captured calls, and keeps all private
records on the local machine.

Part of the local-agent security trial: the upstream SafeAgents proxy and
atif-scan detect, a local decision model judges, and this plugin surfaces
observations, review and stack health in the Hermes desktop UI.
Evaluation and benchmark work lives separately in
[`Enferlain/safeagents-eval`](https://github.com/Enferlain/safeagents-eval).

## Status

- Observation with Tier-1 session correlation, desktop review pane, offline
  replay: implemented and verified.
- Contextual enforcement (Tier-2 `pre_tool_call` directives, ALLOW/ASK/DENY):
  designed, deliberately not implemented yet. Nothing here blocks or approves
  actions today.

## Layout

- `src/hermes_safeagents/` — plugin backend and desktop UI source. The deployed
  plugin is a flat copy of this directory's contents:
  backend → default-profile `~/.hermes/plugins/hermes-safeagents/`,
  desktop UI → `%LOCALAPPDATA%/hermes/desktop-plugins/hermes-safeagents/`.
  Trusted runtime scripts (`judge_adapter.py`, `replay_model.py`, `observe.py`,
  `observation.py`, `decision_models.py`, `gguf_metadata.py`,
  `replay_safety.py`) ship inside the package and load only from their own
  directory — never from the state root or an evaluation checkout.
- `tests/` — offline regression suites; synthetic owner-only fixtures only.
- `docs/` — deployment mapping and observation procedures.
- `scripts/check.py` — data-free check driver (temporary HOME, no real models).

## Runtime state

Observation captures, journals, replay logs and the trusted check venv are
runtime state, not source. They live under the plugin data directory
`~/.hermes/hermes-safeagents/` (default profile only), which mirrors the
historical `trial/` layout — `trial/private-observation/`,
`trial/journal.jsonl`, `trial/logs/`, `.venv-trial/`. No state lives inside a
source checkout.

## Development

```bash
uv sync --locked                 # dependency environment (or UV_PROJECT_ENVIRONMENT=.venv-checks)
uv run --locked python scripts/check.py          # full data-free suite
uv run --locked python scripts/check.py --suite ui   # UI suite only
```

Backend tests require Linux/WSL (POSIX ownership semantics, fcntl). The UI
suite requires Node.js 24+.

## Provenance

Extracted from `Enferlain/safeagents-eval` at its `pre-split-baseline` tag;
commit history preserved via git-filter-repo. Upstream SafeAgents is pinned at
`huggingface/safeagents@dcf38e0` (see `pyproject.toml`); upgrades require
re-running the provenance manifest checks.

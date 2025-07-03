# Poetry Migration Plan

> **Owner:** System Architect (Winston)
> **Related Tasks:** choose_package_manager_poetry, establish_monorepo_workspace
> **Status:** Draft – execution ready

---

## 1. Overview

Migrate all Python sub-projects to **Poetry** to unify dependency management and leverage workspace capabilities.

Projects affected:
1. **Root** (`/`) – currently Hatch
2. **mem0** – Hatch
3. **custom-gpt-adapter** – already Poetry (update constraint handled)
4. **mem0/embedchain** – already Poetry

---

## 2. High-Level Steps

| # | Action | Command / Notes |
|---|--------|-----------------|
| 1 | Install Poetry (locally) | `curl -sSL https://install.python-poetry.org | python -` |
| 2 | Convert root project | `cd / && poetry init --name memorybank-monorepo --no-interaction` – then copy deps from old `pyproject.toml` |
| 3 | Remove Hatch sections | Delete `[build-system]` Hatch config; add `[tool.poetry]` per template |
| 4 | Convert **mem0** | `cd mem0 && poetry init --name mem0 --no-interaction` – import deps |
| 5 | Add both projects to workspace | In root `pyproject.toml`, add path deps (see blueprint) |
| 6 | Set in-project venvs | `poetry config virtualenvs.in-project true` |
| 7 | Lock | `poetry lock -n` at repo root |
| 8 | Run tests | `poetry run pytest` |
| 9 | Commit | `git add . && git commit -m "feat: migrate to Poetry workspace"` |

---

## 3. Root `pyproject.toml` Template

```toml
[tool.poetry]
name = "memorybank-monorepo"
version = "0.0.0"
description = "Poetry workspace aggregator"
packages = []

[tool.poetry.dependencies]
python = ">=3.9,<4.0"
custom-gpt-adapter = { path = "custom-gpt-adapter", develop = true }
mem0 = { path = "mem0", develop = true }
embedchain = { path = "mem0/embedchain", develop = true }

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

---

## 4. CI Update Snippet

```yaml
- name: Set up Poetry
  uses: abatilo/actions-poetry@v3
- name: Install
  run: poetry install --all-extras --no-root
```

---

## 5. Rollback Plan

If migration blocks builds:
1. Revert branch.
2. Continue using Hatch until issues resolved.

---

*End of Plan* 
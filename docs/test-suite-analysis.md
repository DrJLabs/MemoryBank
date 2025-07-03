# MemoryBank – Test‑Suite Analysis & Optimization Roadmap  
_Last updated: 2025‑07‑03 • version v03 (licence‑aware overhaul)_

> **Status:** Living artefact maintained by the BMAD Orchestrator.  
> Source history up‑to‑2025‑07‑03 captured in previous revision.:contentReference[oaicite:0]{index=0}

---

## 1 Objectives

| # | Goal |
|---|------|
| 1 | Achieve and enforce **≥ 80 % statement coverage** across the monorepo. |
| 2 | Establish **≥ 30 % mutation‑score (Phase‑2)** and **≥ 60 % (Phase‑3)** to prove test effectiveness. |
| 3 | Keep CI wall‑time ≤ 8 minutes via parallel execution and test isolation. |
| 4 | Verify **long‑term memory integrity** for both back‑ends:<br> • **PostgreSQL 16 + pgvector** (default OSS stack)<br> • **Qdrant 1.x** (Apache‑2.0 optional module) |
| 5 | Guarantee OSS licence compliance & predictable cost (section 9). |
| 6 | Enforce all quality gates through **branch protection + Mergify merge‑queue** automation. |

---

## 2 Current Inventory (snapshot)

| Area / Stack | Directory | Coverage | Key Gaps |
|--------------|-----------|----------|----------|
| **MemoryBank Core (Python)** | `tests/` | ~65 % | Flaky DB isolation, no perf tests |
| **Custom GPT Adapter** | `custom-gpt-adapter/tests/` | ~55 % | Missing property‑based, fuzz, perf |
| **Vector Store – Postgres + pgvector** | `tests/vector_pg/` (planned) | 0 % | Needs live container tests |
| **Vector Store – Qdrant** | `tests/vector_qdrant/` | ~50 % | Live tests planned, perf missing |
| **mem0 TypeScript libs** | `mem0/**/tests/` | ~40 % | No E2E / contract tests |
| **Monitoring / Metrics** | `monitoring/`, `scripts/` | 0 % | No tests at all |
| **Infrastructure / Docker** | `docker/`, `server/` | 0 % | No smoke / testinfra |
| **BMAD Agents & CLI** | `.bmad-core`, `scripts/` | ~25 % | Behaviour & property tests absent |

---

## 3 Gap‑Priority Matrix (updated)

| Priority | Gap | Mitigation Plan |
|----------|-----|-----------------|
| **P0** | Flaky integration tests (shared DB state) | Ephemeral Postgres fixture; enable `pytest-randomly`. |
| **P0** | Coverage not enforced (currently 62 %) | Add `--cov --cov-fail-under=80` check in CI. |
| **P0** | No licence/compliance scanning | Add FOSSA / OSS‑Review‑Toolkit job. |
| **P1** | No live Postgres + pgvector tests | docker‑compose svc spun up in CI; CRUD + durability tests. |
| **P1** | No structured fuzz / security tests | Hypothesis + Atheris harness on `/api/v1/search`. |
| **P2** | No mutation testing | Mutmut (Py) / Stryker (TS) – 30 % gate. |
| **P2** | No load/perf regression gate | Locust (100 RPS, p95 < 250 ms). |

---

## 4 Recommended Best‑Practice Upgrades

1. **Property‑based testing first‑class** (Hypothesis / fast‑check).  
2. **Dual‑mode live vector‑store harness** (Postgres + pgvector _or_ Qdrant).  
3. **Mutation testing as KPI** (Mutmut & Stryker).  
4. **Structured fuzz / adversarial suites** for API & LLM prompt paths.  
5. **Perf regression gate** – nightly Locust run, block on >10 % latency delta.  
6. **Licence‑compliance CI job** – fail on non‑approved licences.

---

## 5 Phased Roadmap

| Phase | Exit Criteria |
|-------|---------------|
| **1 (done)** | Inventory + gap analysis captured. |
| **2 (active)** | • Module checklists finalised<br>• Coverage gate active<br>• Flaky tests fixed<br>• OSS licence scan passing<br>• Live Postgres + pgvector harness merged |
| **3** | • Mutation ≥ 30 %<br>• Live Qdrant parity tests<br>• Locust perf gate merged<br>• Branch‑protection & Mergify rules live |
| **4 (rolling)** | • Mutation ≥ 60 %<br>• Perf gate enforced<br>• AI‑generated test suggestions auto‑triaged |

---

## 6 Implementation Plan (2025‑07 timeline)

> **Owners** remain **TBD** until agents and additional devs join.

### **Sprint‑0 (ends 2025‑07‑10)**
| Action ID | Action | Notes |
|-----------|--------|-------|
| S0‑CG | Add coverage‑gate (≥ 80 %) via `pytest‑cov` & Jest coverage. | |
| S0‑PAR | Enable parallel CI (`pytest-xdist`, Jest maxWorkers, GHA matrix). | |
| S0‑FLKY | Fix DB flakiness (`tests/integration/test_reset_manager.py`). | |
| S0‑LIC | Integrate **FOSSA / ORT** licence scanning in CI. | |

### **Sprint‑1 (2025‑07‑11 → 07‑24)**
| ID | Action |
|----|--------|
| S1‑HYP | Add ≥ 10 Hypothesis suites on payload validators. |
| S1‑FC | Add ≥ 10 fast‑check suites to mem0‑TS critical utils. |
| S1‑PGV | docker‑compose service: Postgres 16 + pgvector; CRUD & durability tests. |
| S1‑QDR | Optional flag to spin up Qdrant for smoke‑parity run. |

### **Sprint‑2 (07‑25 → 08‑07)**
| ID | Action |
|----|--------|
| S2‑SCH | Schemathesis contract harness on `/api/v1/search`. |
| S2‑INFRA | pytest‑testinfra on Dockerfile; `promtool test rules`. |
| S2‑MUT | Mutmut (30 %) + Stryker initial gate. |
| S2‑DRY | Consolidate duplicate `test_memory_bank_client.py` fixtures. |

### **Phase‑3 Kickoff**
| ID | Action |
|----|--------|
| P3‑LOC | Locust perf suite (100 RPS, p95 < 250 ms) + CI gate. |
| P3‑MUT60 | Raise mutation gate to ≥ 60 %. |
| P3‑MRGQ | Mergify merge‑queue + full branch‑protection enforcement. |

---

## 7 Branch‑Protection & Mergify Rules

* **Required checks:** `tests`, `coverage‑gate`, `CodeQL`, `Dependency‑Gates`, `Licence‑Scan`, `Mutmut`, `Stryker`, `Perf‑baseline` (nightly).  
* **Require branch up‑to‑date** before merge (Mergify strict‑smart rebase).  
* **Reviews:** ≥ 1 human reviewer for non‑bot PRs.  
* **Bot PRs:** label `automerge`, author `BMAD‑bot`; merged automatically when all required checks succeed.

```yaml
# .mergify.yml (excerpt)
pull_request_rules:
  - name: fast‑track trusted bot PRs
    conditions:
      - author=BMAD-bot
      - label=automerge
      - status-success=tests
      - status-success=coverage-gate
      - status-success=Licence-Scan
    actions:
      merge:
        method: squash
        strict: smart+fasttrack
        commit_message: title+body

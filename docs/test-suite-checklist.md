
---

### ✅ `docs/test-suite-checklist.md`
```markdown
# MemoryBank – Test‑Suite Execution Checklist  
_Last updated: 2025‑07‑03 (sync v03)_  :contentReference[oaicite:1]{index=1}

> **Legend**  `[x]` completed  `[~] in progress  `[ ] pending  
> Update boxes (and IDs) as work proceeds. _Owners remain **TBD**._

---

## Master Tasks

- [x] **T1** – Collect current test inventory
- [x] **T2** – Map modules/components to tests
- [x] **T3** – Perform gap analysis
- [x] **T4** – Maintain `test-suite-analysis.md`
- [x] **T5** – Research best practices & next‑gen techniques
- [x] **T6** – Produce per‑module checklists
- [ ] **T7** – Execute roadmap & track progress (ETA 2025‑08‑07)

---

## Sprint‑0 (⏳ → 2025‑07‑10)

| ID | Task | Status |
|----|------|--------|
| **S0‑CG** | Coverage‑gate ≥ 80 % (`pytest‑cov`, Jest) | [~] |
| **S0‑PAR** | Parallel CI (`xdist`, matrix) | [~] |
| **S0‑FLKY** | Fix flaky DB isolation tests | [~] |
| **S0‑LIC** | Integrate FOSSA / ORT licence scan | [ ] |

---

## Sprint‑1 (07‑11 → 07‑24)

| ID | Task | Status |
|----|------|--------|
| **S1‑HYP** | Add ≥ 10 Hypothesis suites | [ ] |
| **S1‑FC**  | Add ≥ 10 fast‑check suites | [ ] |
| **S1‑PGV** | Live Postgres + pgvector docker‑svc tests | [ ] |
| **S1‑QDR** | Optional Qdrant smoke parity | [ ] |

---

## Sprint‑2 (07‑25 → 08‑07)

| ID | Task | Status |
|----|------|--------|
| **S2‑SCH** | Schemathesis contract harness | [ ] |
| **S2‑INFRA** | pytest‑testinfra + promtool rules | [ ] |
| **S2‑MUT** | Mutmut 30 % + Stryker setup | [ ] |
| **S2‑DRY** | Consolidate duplicate client tests | [ ] |

---

## Phase‑3 Preparation (ETA after 08‑07)

| ID | Task | Status |
|----|------|--------|
| **P3‑LOC** | Locust perf gate (100 RPS) | [ ] |
| **P3‑MUT60** | Raise mutation gate ≥ 60 % | [ ] |
| **P3‑MRGQ** | Mergify merge‑queue rules live | [ ] |

---

> **How to update:**  
> 1. Edit this file in every PR that starts (`[~]`) or finishes (`[x]`) a checklist item.  
> 2. Keep IDs consistent with `.cursor-todo.json` for automation.  
> 3. When Sprint‑targets move, add new sections and archive completed ones.

---

_Maintainer: **BMAD Orchestrator**_  

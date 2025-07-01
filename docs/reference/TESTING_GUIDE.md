# 🧪 Memory-C* Testing & QA Guide (Canonical)

**Status**: Authoritative reference for all quality-assurance practices.  
**Last Updated**: 2025-07-01

> All documentation SHOULD link here for testing details. Information elsewhere may summarise but MUST defer to this guide.

---

## 🎯 Goals & Philosophy

1. **High Confidence Releases** – Maintain ≥80 % test coverage and automated regression protection.  
2. **AI-Enhanced Validation** – Blend traditional pytest with AI-driven self-correction and adaptive test selection.  
3. **Continuous Learning** – Feed test insights back into the Memory system (`ai-add-smart`) for future agents.  
4. **Fast Feedback** – Keep local test runs <5 minutes and CI runs <10 minutes.

---

## 🗂️ Test Layers & Responsibilities

| Layer | Location | Framework | Purpose |
|-------|----------|-----------|---------|
| **Unit Tests** | `tests/unit/` | `pytest`, `hypothesis` | Validate individual functions & classes |
| **Integration Tests** | `tests/integration/` | `pytest-asyncio` | Verify component interactions (API ↔ DB, adapters ↔ OpenMemory) |
| **ML Regression Tests** | `tests/ml/` | `pytest`, `scikit-learn` | Detect model drift & accuracy regressions for `phase5-advanced-ai-predictive.py` |
| **E2E / Smoke Tests** | `tests/e2e/` | `pytest`, `httpx` | Exercise core user journeys via REST endpoints |
| **Self-Correcting AI Tests** | `tests/ai/ai_testing_framework.py` | Custom AI framework | Automatically propose fixes on failures & update memories |

---

## 🔧 Running Tests Locally

```bash
# Activate environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements-testing.txt

# Run all tests
pytest -m "not slow" -n auto

# Run AI-enhanced self-correcting suite
python tests/ai/ai_testing_framework.py

# Generate coverage report
pytest --cov=mem0 --cov=openmemory --cov-report=term-missing
```

> **Tip:** Use `pytest -m slow` for long-running ML regression tests when needed.

---

## 🤖 AI-Enhanced Testing Workflow

```mermaid
graph LR
    A[Code / Config Change] --> B[Run pytest suites]
    B --> |Failures?|
    C{Fail}
    C -->|Yes| D[AI Self-Correction Engine]
    C -->|No| G[Store Insights]
    D --> E[Generate Patch & Re-run]
    E --> |Success?| F{Pass}
    F -->|Yes| G
    F -->|No| H[Fail CI Pipeline]
    G --> I[ai-add-smart "TEST: insights"]
```

1. **Failure Detection** – Standard pytest identifies failures.  
2. **Self-Correction** – `ai_testing_framework.py` attempts to auto-patch trivial issues (import errors, typos).  
3. **Patch Validation** – Re-runs failing tests; if success the patch is committed automatically (CI bot).  
4. **Memory Storage** – Stores test insights to improve future AI agent context.

---

## 🏗️ CI/CD Integration

* **Platform:** GitHub Actions (`.github/workflows/ci.yml`).  
* **Steps:**
  1. Checkout → Setup Python → Install deps  
  2. `pytest -n auto --cov`  
  3. `python tests/ai/ai_testing_framework.py`  
  4. Upload coverage & artifacts  
  5. On failure, create GitHub issue & comment with AI suggestions.
* **Gates:** Merge blocked unless all tests pass **and** coverage ≥ target.

---

## 📊 Coverage Targets & Metrics

| Component | Current | Target |
|-----------|---------|--------|
| mem0 core | 65 % | 80 % |
| openmemory | 55 % | 80 % |
| Adapter services | 70 % | 90 % |
| Overall | **60 %** | **≥80 %** |

Coverage reports are generated with `pytest --cov` and persisted as CI artifacts.

---

## 🛠️ Tooling & Dependencies

* `pytest`, `pytest-asyncio`, `pytest-cov`, `hypothesis`  
* `scikit-learn`, `numpy`, `pandas` (ML regression)  
* Custom **AI Testing Framework** (`tests/ai_testing_framework.py`)  
* `httpx`, `tenacity` for integration & E2E tests  

Install all via `requirements-testing.txt`.

---

## 🧠 Memory Integration Patterns

```python
# Example pattern inside a test
result = some_function()
assert result == expected
ai_add_smart(f"TEST_PASSED: some_function returned {result}")
```

1. **Before CI start** – `ai-ctx-tech "testing patterns"` for historic context.  
2. **After suite** – Store insights with `ai-add-smart`.

---

## 🔄 Updating This Guide

1. Modify this file for significant strategy changes.  
2. Increment coverage targets only when consistently met.  
3. Ensure any new test layer is documented here first.

---

## 🔗 Related Documents

* **Integration Patterns:** [`../WORKFLOWS/INTEGRATION_PATTERNS.md`](../WORKFLOWS/INTEGRATION_PATTERNS.md)  
* **Project Dashboard:** [`../PROJECT_CONTROL_CENTER.md`](../PROJECT_CONTROL_CENTER.md)  
* **Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)

---

**Quality Status:** ACTIVE  
**Coverage Trend:** 📈 improving  
**Next Goal:** Achieve ≥80 % overall coverage and fully automate self-corrections.
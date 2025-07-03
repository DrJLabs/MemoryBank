# Dependency Governance Policy

> **Owner:** System Architect (Winston)
> **Related Tasks:** implement_dependency_policies, establish_monorepo_workspace
> **Status:** Draft – awaiting approval

---

## 1. Purpose

This policy defines how the MemoryBank monorepo manages third-party dependencies to ensure **security**, **stability**, and **maintainability** across all services.

---

## 2. Scope

Applies to all sub-projects within the MemoryBank repository:
- Python packages managed by **Poetry**.
- JavaScript/TypeScript packages managed by **pnpm**.
- Docker images & OS packages referenced in Dockerfiles.

---

## 3. Version Strategy

- **Critical security patches**: Apply **immediately** once disclosed.
- **All other updates**: Upgrade **opportunistically** (e.g., when a feature is needed or during monthly maintenance).

---

## 4. Approval & Merge Workflow

Since there is currently a **single maintainer**, the process is lightweight:
1. Open branch or automated PR with dependency bump details.
2. Run local tests (`pytest`, `pnpm test`).
3. If tests pass and no critical vulnerabilities, **self-merge**.

---

## 5. Security Scanning

- Run **Safety** (Python) and **Trivy** (containers) **monthly** *or* before any production deployment.
- For JavaScript lock files, run `pnpm audit` on the same schedule.
- Address vulnerabilities with CVSS ≥ 7.0 before release.

---

## 6. Quality Gates

- All unit/integration tests must pass.
- No open **critical** vulnerabilities (CVSS ≥ 9.0).
- Regenerate lock files (`poetry lock -n`, `pnpm install`) when upgrading.

---

## 7. Documentation Requirements

Each service's README must list:
- How to add/update dependencies.
- Link to this policy.

---

## 8. Roles & Responsibilities

| Role | Responsibility |
|------|----------------|
| **Maintainer (you)** | Owns policy, performs upgrades, runs scans, merges PRs |

---

## 9. Exceptions

Log any temporary deferment of a vulnerability fix in `docs/exceptions/DEP-<date>-defer.md` with rationale.

---

## 10. Review Cycle

Policy reviewed every **6 months** or after major incident.

---

*End of Policy* 
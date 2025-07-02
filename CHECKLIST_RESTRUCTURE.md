# MemoryBank Restructure Master Checklist

> **Purpose:** Practical, ordered checklist for agents executing the full platform restructure in alignment with `DEPENDENCY_ANALYSIS_REPORT.md` and existing `todo_write` tasks.

| # | Task ID | Description | Owner | Status |
|---|---------|-------------|--------|--------|
| 1 | standardize_python_versions | Standardize Python version to `>=3.9,<4.0` in all `pyproject.toml` files | Architect / DevOps | ☐ |
| 2 | align_pytest_versions | Align pytest to `>=8.0.0` across project | QA Lead | ☐ |
| 3 | update_fastapi_uvicorn | Upgrade FastAPI + Uvicorn to current stable versions | Backend Lead | ☐ |
| 4 | generate_lock_files | Generate/refresh lock files (`poetry.lock`, compiled requirements) | DevOps | ☐ |
| 5 | choose_package_manager_poetry | Decide & document Poetry as single Python package manager | Architect | ☐ |
| 6 | migrate_projects_to_poetry | Migrate root, mem0, custom-gpt-adapter, embedchain to Poetry | Backend Lead | ☐ |
| 7 | consolidate_requirements_files | Centralize scattered `requirements*.txt` into `dependencies/` directory | DevOps | ☐ |
| 8 | add_security_scanning | Integrate Safety, Bandit, Semgrep into CI pipelines | Security | ☐ |
| 9 | configure_dependabot | Add Dependabot config for pip & npm ecosystems | DevOps | ☐ |
| 10 | implement_dependency_policies | Formalize dependency governance (age, patch window, pinning) | Architect | ☐ |
| 11 | establish_monorepo_workspace | Add Poetry & pnpm workspace settings for monorepo | Architect | ☐ |
| 12 | implement_dependency_quality_gates | Add dependency gates to CI/CD (vulnerability & freshness checks) | DevOps | ☐ |
| 13 | track_success_metrics | Implement monitoring dashboards for success metrics | QA / DevOps | ☐ |

---

## Usage Instructions
1. **Claim a task** by setting your name in **Owner**.
2. **Update Status** using:
   - ☐ Pending
   - 🚧 In-Progress
   - ✅ Completed
3. **Link Pull Requests** in the Description once a task is in review.
4. **Maintain Dependencies**: some tasks depend on others—see the dependency list in `todo_write`.

---

## References
- [`DEPENDENCY_ANALYSIS_REPORT.md`](./DEPENDENCY_ANALYSIS_REPORT.md)
- [Project Audit & Review Checklist](https://www.slideshare.net/slideshow/project-audit-review-checklist/12998606)
- [Dependency Management Best Practices](https://medium.com/inside-bukalapak/the-chaos-of-maintaining-software-dependencies-and-how-to-tame-them-413cc233d800) 
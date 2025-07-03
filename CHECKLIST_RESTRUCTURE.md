# MemoryBank Restructure Master Checklist

> **Purpose:** Practical, ordered checklist for agents executing the full platform restructure in alignment with `DEPENDENCY_ANALYSIS_REPORT.md` and existing `todo_write` tasks.

| # | Task ID | Description | Owner | Status |
|---|---------|-------------|--------|--------|
| 1 | standardize_python_versions | Standardize Python version to `>=3.9,<4.0` in all `pyproject.toml` files | AI Agent | ✅ |
| 2 | align_pytest_versions | Align pytest to `>=8.0.0` across project | Backend Lead | ✅ |
| 3 | update_fastapi_uvicorn | Upgrade FastAPI + Uvicorn to current stable versions | Backend Lead | ✅ |
| 4 | generate_lock_files | Generate/refresh lock files (`poetry.lock`, compiled requirements) | AI Agent | ✅ |
| 5 | choose_package_manager_poetry | Decide & document Poetry as single Python package manager | AI Agent | ✅ |
| 6 | migrate_projects_to_poetry | Migrate root, mem0, custom-gpt-adapter, embedchain to Poetry | AI Agent | ✅ |
| 7 | consolidate_requirements_files | Centralize scattered `requirements*.txt` into `dependencies/` directory | AI Agent | ✅ |
| 8 | add_security_scanning | Integrate Safety, Bandit, Semgrep into CI pipelines | AI Agent | ✅ |
| 9 | configure_dependabot | Add Dependabot config for pip & npm ecosystems | AI Agent | ✅ |
| 10 | implement_dependency_policies | Formalize dependency governance (age, patch window, pinning) | AI Agent | ✅ |
| 11 | establish_monorepo_workspace | Add Poetry & pnpm workspace settings for monorepo | AI Agent | ✅ |
| 12 | resolve_database_connectivity | Database connectivity issues resolved - configured tests to use mem0 PostgreSQL database | AI Agent | ✅ |
| 13 | configure_test_environment | Test environment configured with pytest-env plugin and automatic database connection variables | AI Agent | ✅ |
| 14 | fix_auth_test_logic | Fix auth endpoint test failures (401/404 errors) - functional issues beyond database connectivity | Backend Lead | ✅ |
| 15 | fix_memory_schema_constraints | Fix memory operation tests - resolve NotNull constraint violations in custom_gpt_applications table | Backend Lead | ✅ |
| 16 | fix_bmad_framework_tests | Fix BMAD framework tests - resolve KeyError exceptions in orchestrator and memory performance tests | AI Agent | ✅ |
| 17 | security_vulnerability_review | Address security vulnerabilities found in Trivy scan (h11, torch, transformers, setuptools, etc.) | AI Agent | ✅ |
| 18 | implement_dependency_quality_gates | Add dependency gates to CI/CD (vulnerability & freshness checks) | AI Agent | ✅ |
| 19 | track_success_metrics | Implement monitoring dashboards for success metrics | AI Agent | ✅ |

---

## Recent Achievements ✅
- **Database Infrastructure**: Successfully leveraged existing mem0 PostgreSQL database (localhost:8432)
- **Test Environment**: Automated database connection configuration with pytest-env plugin
- **Poetry Migration**: All major components migrated to Poetry workspace structure
- **Dependency Governance**: Simplified policy documented and implemented
- **Test Connectivity**: Eliminated all database connectivity test failures

## Current Focus Areas 🚧
- **Test Functionality**: Resolving auth endpoint logic and schema constraint issues
- **Security**: Addressing Trivy-identified vulnerabilities in dependencies
- **BMAD Framework**: Fixing KeyError exceptions in test orchestrator

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
- [`docs/DATABASE_SETUP_SOLUTION.md`](./docs/DATABASE_SETUP_SOLUTION.md)
- [`docs/Poetry_Migration_Plan.md`](./docs/Poetry_Migration_Plan.md)
- [`docs/Dependency_Governance_Policy.md`](./docs/Dependency_Governance_Policy.md)
- [`docs/MONITORING_SETUP.md`](./docs/MONITORING_SETUP.md)
- [Project Audit & Review Checklist](https://www.slideshare.net/slideshow/project-audit-review-checklist/12998606)
- [Dependency Management Best Practices](https://medium.com/inside-bukalapak/the-chaos-of-maintaining-software-dependencies-and-how-to-tame-them-413cc233d800) 
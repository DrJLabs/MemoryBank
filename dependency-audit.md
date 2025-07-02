# Dependency Audit Report - MemoryBank Repository

Generated: January 2025

## Executive Summary

The MemoryBank repository contains multiple projects with dependencies across Python and JavaScript ecosystems. A comprehensive security scan has revealed **120 vulnerabilities** across the codebase, including:

- **16 CRITICAL** vulnerabilities
- **44 HIGH** vulnerabilities  
- **45 MEDIUM** vulnerabilities
- **15 LOW** vulnerabilities

Immediate action is required to address critical vulnerabilities, particularly in:
- `gradio` (4.11.0) - Multiple critical CVEs
- `h11` (0.14.0) - Critical CVE-2025-43859
- `torch` (2.3.0) - Critical CVE-2025-32434
- `embedchain` (various versions) - Critical CVE-2024-23731
- `next` (13.4.9) - Critical CVE-2025-29927

## Repository Structure

The repository contains multiple sub-projects:

1. **Root Project** (`/pyproject.toml`)
   - Testing framework dependencies
   - Development tools

2. **Custom GPT Adapter** (`/custom-gpt-adapter/`)
   - FastAPI-based service
   - PostgreSQL integration
   - Redis/Celery for async tasks

3. **Mem0 Core** (`/mem0/`)
   - AI memory management system
   - Multiple vector database integrations
   - LLM integrations

4. **OpenMemory UI** (`/mem0/openmemory/ui/`)
   - Next.js 15.2.4 application
   - React 19 with Redux Toolkit
   - Radix UI components

5. **Vercel AI SDK** (`/mem0/vercel-ai-sdk/`)
   - AI provider integrations
   - Memory capabilities for LLMs

6. **Embedchain Examples** (`/mem0/embedchain/`)
   - Multiple example applications
   - Legacy dependencies with vulnerabilities

## Critical Vulnerabilities Summary

### 1. Gradio (4.11.0) - CRITICAL
**Location:** `mem0/embedchain/embedchain/deployment/gradio.app/requirements.txt`

- **CVE-2023-6572** (CRITICAL) - Fixed in 4.14.0
- **CVE-2025-23042** (CRITICAL) - Fixed in 5.11.0  
- **GHSA-m842-4qm8-7gpq** (CRITICAL) - Fixed in 4.19.2
- Plus 13 HIGH and 13 MEDIUM vulnerabilities

**Recommendation:** Upgrade to latest version 5.31.0 or at minimum 5.11.0

### 2. H11 (0.14.0) - CRITICAL
**Location:** Multiple poetry.lock files

- **CVE-2025-43859** (CRITICAL) - Fixed in 0.16.0

**Recommendation:** Upgrade to 0.16.0 immediately

### 3. PyTorch (2.3.0) - CRITICAL
**Location:** `mem0/embedchain/poetry.lock`

- **CVE-2025-32434** (CRITICAL) - Fixed in 2.6.0

**Recommendation:** Upgrade to 2.6.0 or latest stable

### 4. Embedchain (Multiple versions) - CRITICAL
**Locations:** Various example requirements.txt files

- **CVE-2024-23731** (CRITICAL) - Fixed in 0.1.57
- Versions affected: 0.0.58, 0.1.3, 0.1.31

**Recommendation:** Upgrade all instances to 0.1.57 or remove if examples are not needed

### 5. Next.js (13.4.9) - CRITICAL  
**Location:** `mem0/embedchain/examples/full_stack/frontend/`

- **CVE-2025-29927** (CRITICAL) - Fixed in 13.5.9, 14.2.25, 15.2.3
- Plus 5 HIGH vulnerabilities

**Recommendation:** Upgrade to 15.2.3 (latest stable)

## High Priority Updates

### Python Dependencies

1. **setuptools** (70.3.0, 78.1.0) - CVE-2025-47273 (HIGH)
   - Upgrade to 78.1.1

2. **transformers** (4.42.4) - Multiple HIGH CVEs
   - Upgrade to 4.50.0

3. **starlette** (0.37.2) - CVE-2024-47874 (HIGH)
   - Upgrade to 0.40.0

4. **protobuf** (4.25.3, 5.29.4) - CVE-2025-4565 (HIGH)
   - Upgrade to 5.29.5 or 6.31.1

5. **mysql-connector-python** (8.4.0) - CVE-2024-21272 (HIGH)
   - Upgrade to 9.1.0

### JavaScript Dependencies

1. **axios** (1.7.7, 1.8.4) - CVE-2025-27152 (HIGH)
   - Upgrade to 1.8.2

2. **tar-fs** (2.1.2) - CVE-2025-48387 (HIGH)
   - Upgrade to 2.1.3 or 3.0.9

3. **braces** (3.0.2) - CVE-2024-4068 (HIGH)
   - Upgrade to 3.0.3

4. **cross-spawn** (7.0.3) - CVE-2024-21538 (HIGH)
   - Upgrade to 7.0.5

## Medium Priority Updates

### Common Patterns

1. **urllib3** - Multiple versions affected by CVE-2025-50181/50182
   - Upgrade all instances to 2.5.0

2. **requests** - CVE-2024-47081 affecting 2.31.0, 2.32.3
   - Upgrade to 2.32.4

3. **jinja2** (3.1.4) - Multiple MEDIUM CVEs
   - Upgrade to 3.1.6

4. **streamlit** (1.29.0) - CVE-2024-42474
   - Upgrade to 1.37.0

## Dependency Version Conflicts

Several dependencies have version conflicts across sub-projects:

1. **pydantic**: 2.7.3 (mem0) vs 2.10.4 (server)
2. **fastapi**: 0.110.0 (custom-gpt-adapter) vs 0.115.8 (server)
3. **uvicorn**: 0.27.1 (custom-gpt-adapter) vs 0.34.0 (server)

## Recommendations

### Immediate Actions (Critical)

1. **Update all critical vulnerabilities** within 48 hours
2. **Remove or update embedchain examples** - they contain numerous vulnerabilities
3. **Upgrade gradio** to 5.31.0 across all projects
4. **Update h11** to 0.16.0 in all Python projects

### Short-term Actions (1 week)

1. **Standardize dependency versions** across sub-projects
2. **Update all HIGH vulnerabilities**
3. **Implement dependency pinning** for production deployments
4. **Set up automated vulnerability scanning** in CI/CD

### Long-term Actions (1 month)

1. **Establish dependency update policy**
2. **Implement automated dependency updates** (e.g., Dependabot, Renovate)
3. **Create security response procedures**
4. **Regular quarterly dependency audits**

## Best Practices Implementation

Based on [Renovate's upgrade best practices](https://docs.renovatebot.com/upgrade-best-practices/) and [GitHub's dependency management guide](https://docs.github.com/en/code-security/dependabot/maintain-dependencies/best-practices-for-maintaining-dependencies):

1. **Use automated tools**: Implement Renovate or Dependabot
2. **Update frequently**: Small, regular updates are easier than large batches
3. **Pin dependencies**: Use exact versions in production
4. **Test thoroughly**: Automated tests for all dependency updates
5. **Monitor actively**: Set up alerts for new vulnerabilities

## Tools Used

- **Codacy Trivy Scanner** v0.59.1 - Comprehensive vulnerability detection
- **SARIF format** - Standardized security findings
- **Multiple vulnerability databases**: CVE, GHSA, OSV

---

*This report should be reviewed by the security team and development leads. Priority should be given to CRITICAL and HIGH vulnerabilities affecting production systems.* 
# PostgreSQL v16 Baseline Discovery & Upgrade Checklist

> **Purpose:** Ensure smooth upgrade to PostgreSQL v16 by collecting environment details and verifying pgvector compatibility.

| # | Task ID | Description | Owner | Status |
|---|---------|-------------|-------|-------|
| 1 | baseline_discovery | Capture baseline environment details before v16 upgrade |  | ☐ Pending |
| 2 | cluster_inventory | Run `psql -Atc "select version(), current_setting('data_directory')"` against each environment to record version info, extensions, and data directories |  | ☐ Pending |
| 3 | extension_matrix | Export `pg_available_extensions`; flag extensions not validated on v16 |  | ☐ Pending |
| 4 | pgvector_gap_check | Verify pgvector 0.8 cost-estimation and HNSW improvements; document any query plan changes |  | ☐ Pending |
| 5 | touchstone_perf_benchmark | Run 10‑minute `pgbench` with ANN queries on current prod snapshot to establish baseline TPS/latency |  | ☐ Pending |

## Usage Instructions
1. **Claim a task** by setting your name in **Owner**.
2. **Update Status** using:
   - ☐ Pending
   - 🚧 In-Progress
   - ✅ Completed
3. **Link Pull Requests** in the Description once a task is in review.
4. **Keep benchmark results** in the project's `/reports` directory.

---

Last Updated: 2025-06-27

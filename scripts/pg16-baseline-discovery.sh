#!/bin/bash
set -euo pipefail

OUTPUT_DIR="$(cd "$(dirname "$0")/.." && pwd)/reports/pg16"
mkdir -p "$OUTPUT_DIR"
OUTPUT_FILE="$OUTPUT_DIR/baseline_$(date +%Y%m%d_%H%M%S).md"

{
  echo "# PostgreSQL v16 Baseline Discovery"
  echo ""
  echo "**Generated:** $(date -u +"%Y-%m-%d %H:%M:%SZ")"
  echo ""
  echo "## System Information"
  echo ""
  if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "- **OS:** $PRETTY_NAME"
  else
    echo "- **OS:** Unknown"
  fi
  echo "- **Kernel:** $(uname -r)"
  echo "- **Architecture:** $(uname -m)"
  echo "- **CPU(s):** $(nproc)"
  echo "- **Memory:** $(free -h | awk '/Mem:/ {print $2 " total, " $3 " used"}')"
  echo "- **Disk:** $(df -h / | awk 'NR==2 {print $2 " total, " $4 " free"}')"
  echo ""
  echo "## PostgreSQL"
  echo ""
  if command -v psql >/dev/null 2>&1; then
    echo "- **psql version:** $(psql --version | awk '{print $NF}')"
  else
    echo "- **psql version:** Not installed"
  fi
  echo ""
  echo "## Environment Variables"
  echo ""
  env | grep -E '^(PG|POSTGRES|DB)' | sort || true
} > "$OUTPUT_FILE"

echo "Baseline discovery saved to $OUTPUT_FILE"

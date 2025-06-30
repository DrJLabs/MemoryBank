#!/usr/bin/env bash
# restart_bmad_api.sh
# Gracefully restarts the BMAD Tracking API located in mem0/openmemory/bmad-tracking-api.py.

set -euo pipefail

# -------- Configuration --------
API_DIR="mem0/openmemory"            # Directory containing the API entrypoint
API_ENTRY="bmad-tracking-api.py"    # Entrypoint script relative to API_DIR
PORT=8767                             # Port the API listens on
LOGFILE="bmad_api.log"              # Log file in repo root

# Attempt to activate a virtualenv if one exists at project root
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
if [[ -f "$PROJECT_ROOT/.venv/bin/activate" ]]; then
  VENV_ACTIVATE="source $PROJECT_ROOT/.venv/bin/activate"
else
  VENV_ACTIVATE=":"
fi

# -------- Functions --------
function stop_running_instance() {
  local pid
  pid=$(lsof -t -i:"${PORT}" || true)
  if [[ -n "$pid" ]]; then
    echo "→ Found running instance (pid $pid). Sending SIGTERM…"
    kill -15 "$pid"
    # Wait up to 10 seconds for graceful shutdown
    for _ in {1..10}; do
      if ps -p "$pid" > /dev/null; then
        sleep 1
      else
        break
      fi
    done
    # Force kill if still alive
    if ps -p "$pid" > /dev/null; then
      echo "⚠️  Process did not exit gracefully, sending SIGKILL."
      kill -9 "$pid"
    else
      echo "✓ Previous instance stopped."
    fi
  else
    echo "ℹ️  No running instance found on port $PORT."
  fi
}

function start_new_instance() {
  echo "→ Starting new instance…"
  (
    eval "$VENV_ACTIVATE"
    cd "$API_DIR" || exit 1
    nohup python "$API_ENTRY" >> "$PROJECT_ROOT/$LOGFILE" 2>&1 &
  )
  # Wait briefly before health-check
  sleep 2
  if curl -fs "http://localhost:${PORT}/api/v1/bmad/health" > /dev/null; then
    echo "✅ BMAD Tracking API is up and healthy."
  else
    echo "❌ API failed to start. Check $LOGFILE for details." >&2
    exit 1
  fi
}

# -------- Main --------
stop_running_instance
start_new_instance 
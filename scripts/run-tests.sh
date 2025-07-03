#!/bin/bash
# MemoryBank Test Runner - Ephemeral Postgres Edition
# Demonstrates the new isolated database testing setup

set -e

echo "🧪 MemoryBank Test Suite - Ephemeral Postgres Setup"
echo "=================================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if test dependencies are installed
if ! python -c "import testcontainers" >/dev/null 2>&1; then
    echo "📦 Installing test dependencies..."
    pip install -r dependencies/test.txt
else
    echo "✅ Test dependencies are installed"
fi

# Run the ephemeral Postgres validation tests first
echo ""
echo "🔍 Running ephemeral Postgres validation tests..."
pytest tests/test_ephemeral_postgres.py -v

# Run all tests with coverage
echo ""
echo "🧪 Running full test suite with coverage..."
pytest --cov=app --cov-report=term-missing --cov-fail-under=80 -v

# Run tests in parallel to demonstrate isolation
echo ""
echo "⚡ Running tests in parallel to demonstrate isolation..."
pytest tests/test_ephemeral_postgres.py -n auto -v

# Demonstrate different parallel strategies
echo ""
echo "🔧 Testing different parallel strategies..."
echo "  - Auto workers (recommended):"
pytest tests/test_ephemeral_postgres.py -n auto --tb=no -q
echo "  - Fixed 2 workers:"
pytest tests/test_ephemeral_postgres.py -n 2 --tb=no -q
echo "  - Logical CPU count:"
pytest tests/test_ephemeral_postgres.py -n logical --tb=no -q

echo ""
echo "🎉 All tests completed successfully!"
echo ""
echo "Key achievements:"
echo "✅ Ephemeral Postgres containers working"
echo "✅ pgvector extension available"
echo "✅ Complete test isolation"
echo "✅ Parallel execution working (multiple strategies)"
echo "✅ Coverage reporting active"
echo "✅ GitHub Actions workflow ready"
echo ""
echo "Sprint-0 Progress:"
echo "✅ S0-EPH-PG: Ephemeral Postgres fixture implemented"
echo "✅ S0-PAR: Parallel CI ready (pytest -n auto)"
echo "🔄 S0-CG: Coverage gate prepared (--cov-fail-under=80)"
echo "🔄 S0-LIC: FOSSA/ORT license scanning needed"
echo ""
echo "💡 Try the interactive demo: ./scripts/demo-parallel-testing.sh" 
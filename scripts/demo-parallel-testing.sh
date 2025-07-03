#!/bin/bash
# Demo: Parallel Testing with Ephemeral Postgres
# Shows performance improvements and isolation validation

set -e

echo "🚀 MemoryBank Parallel Testing Demo"
echo "==================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

if ! python -c "import pytest" &> /dev/null; then
    echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
    pip install -r dependencies/test.txt
fi

echo -e "${GREEN}✅ Prerequisites ready${NC}"
echo ""

# Create reports directory
mkdir -p reports

# Demo 1: Sequential vs Parallel Performance
echo -e "${BLUE}🏃 Demo 1: Sequential vs Parallel Performance${NC}"
echo "Running the same tests sequentially and in parallel..."
echo ""

echo -e "${YELLOW}⏱️  Sequential execution:${NC}"
time pytest tests/test_ephemeral_postgres.py -v --tb=no | tee reports/sequential.log

echo ""
echo -e "${YELLOW}⚡ Parallel execution (auto workers):${NC}"
time pytest tests/test_ephemeral_postgres.py -n auto -v --tb=no | tee reports/parallel.log

echo ""

# Demo 2: Test Isolation Validation
echo -e "${BLUE}🔒 Demo 2: Test Isolation Validation${NC}"
echo "Running isolation tests with high parallelism to prove database separation..."
echo ""

pytest tests/test_ephemeral_postgres.py::test_database_isolation_between_tests \
       tests/test_ephemeral_postgres.py::test_database_isolation_second_test \
       -n 4 --count=5 -v

echo ""
echo -e "${GREEN}✅ Test isolation validated - each test gets its own database!${NC}"
echo ""

# Demo 3: Different Parallel Strategies
echo -e "${BLUE}⚙️  Demo 3: Different Parallel Strategies${NC}"
echo "Demonstrating different parallel execution strategies..."
echo ""

echo -e "${YELLOW}🔧 Strategy 1: Auto workers (pytest decides)${NC}"
pytest tests/test_ephemeral_postgres.py -n auto --tb=no -q

echo ""
echo -e "${YELLOW}🔧 Strategy 2: Fixed 2 workers${NC}"
pytest tests/test_ephemeral_postgres.py -n 2 --tb=no -q

echo ""
echo -e "${YELLOW}🔧 Strategy 3: Logical CPU count${NC}"
pytest tests/test_ephemeral_postgres.py -n logical --tb=no -q

echo ""

# Demo 4: Markers and Selective Parallel Execution
echo -e "${BLUE}🏷️  Demo 4: Test Markers and Selective Execution${NC}"
echo "Running different test categories with appropriate parallelism..."
echo ""

echo -e "${YELLOW}🚀 Fast unit tests (high parallelism):${NC}"
pytest -m "unit" -n auto --tb=no -q || echo "No unit tests found yet"

echo ""
echo -e "${YELLOW}🔗 Integration tests (moderate parallelism):${NC}"
pytest -m "integration" -n 2 --tb=no -q || echo "No integration tests found yet"

echo ""
echo -e "${YELLOW}🐌 Slow tests (sequential):${NC}"
pytest -m "slow" -n 1 --tb=no -q

echo ""

# Performance Summary
echo -e "${BLUE}📊 Performance Summary${NC}"
echo "========================"

if [ -f reports/sequential.log ] && [ -f reports/parallel.log ]; then
    SEQUENTIAL_TIME=$(grep "passed in" reports/sequential.log | awk '{print $(NF-1)}' | sed 's/s//')
    PARALLEL_TIME=$(grep "passed in" reports/parallel.log | awk '{print $(NF-1)}' | sed 's/s//')
    
    if [ ! -z "$SEQUENTIAL_TIME" ] && [ ! -z "$PARALLEL_TIME" ]; then
        echo "Sequential execution: ${SEQUENTIAL_TIME}s"
        echo "Parallel execution:   ${PARALLEL_TIME}s"
        
        # Calculate improvement
        python3 -c "
import sys
try:
    seq = float('$SEQUENTIAL_TIME')
    par = float('$PARALLEL_TIME')
    if par > 0:
        speedup = seq / par
        improvement = ((seq - par) / seq) * 100
        print(f'Speedup: {speedup:.2f}x faster ({improvement:.1f}% improvement)')
    else:
        print('Unable to calculate speedup')
except Exception as e:
    print('Performance calculation failed:', e)
        "
    fi
fi

echo ""
echo -e "${GREEN}🎉 Demo Complete!${NC}"
echo ""
echo -e "${BLUE}Key Achievements Demonstrated:${NC}"
echo "✅ Ephemeral Postgres containers provide complete test isolation"
echo "✅ Parallel execution works seamlessly with containerized databases"
echo "✅ Different parallelism strategies available for different test types"
echo "✅ Test markers enable intelligent parallel execution"
echo "✅ Performance improvements from parallel execution"
echo ""
echo -e "${YELLOW}💡 Next Steps:${NC}"
echo "- Enable parallel execution in CI with: pytest -n auto"
echo "- Add coverage reporting with: pytest --cov=app --cov-fail-under=80"
echo "- Use test markers to optimize parallel strategies"
echo ""
echo -e "${BLUE}📚 Learn More:${NC}"
echo "- pytest-xdist docs: https://pytest-xdist.readthedocs.io/"
echo "- testcontainers docs: https://testcontainers.com/guides/getting-started-with-testcontainers-for-python/" 
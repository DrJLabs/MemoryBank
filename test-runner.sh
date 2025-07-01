#!/bin/bash

# MemoryBank Test Runner - Verification Script
# This script tests the testing framework setup

set -e

echo "🧪 MemoryBank Testing Framework Verification"
echo "=============================================="

# Check dependencies
echo "📋 Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Check pytest
if ! python3 -c "import pytest" 2>/dev/null; then
    echo "⚠️  pytest not found, installing..."
    pip install pytest pytest-cov pytest-html pytest-asyncio pytest-xdist
else
    echo "✅ pytest found: $(python3 -c "import pytest; print(pytest.__version__)")"
fi

# Check Node.js for TypeScript tests
if command -v node &> /dev/null; then
    echo "✅ Node.js found: $(node --version)"
    HAS_NODE=true
else
    echo "⚠️  Node.js not found - TypeScript tests will be skipped"
    HAS_NODE=false
fi

echo ""
echo "🔍 Testing Framework Components..."

# Test 1: Check pytest configuration
echo "Test 1: Checking pytest configuration..."
if [ -f "pyproject.toml" ]; then
    echo "✅ pyproject.toml configuration found"
    
    # Test pytest discovery
    if python3 -m pytest --collect-only -q > /dev/null 2>&1; then
        TEST_COUNT=$(python3 -m pytest --collect-only -q 2>/dev/null | grep "test" | wc -l)
        echo "✅ pytest can discover $TEST_COUNT test items"
    else
        echo "⚠️  pytest discovery issues detected"
    fi
else
    echo "⚠️  pyproject.toml not found - using pytest.ini"
fi

# Test 2: Check test directory structure
echo ""
echo "Test 2: Checking test directory structure..."
TEST_DIRS=("tests" "custom-gpt-adapter/tests" "mem0/tests" "mem0/embedchain/tests")

for dir in "${TEST_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        TEST_FILES=$(find "$dir" -name "test_*.py" -o -name "*_test.py" | wc -l)
        echo "✅ $dir found with $TEST_FILES test files"
    else
        echo "⚠️  $dir not found"
    fi
done

# Test 3: Check custom AI testing framework
echo ""
echo "Test 3: Checking custom AI testing framework..."
if [ -f "tests/ai_testing_framework.py" ]; then
    echo "✅ AI testing framework found"
    
    # Check if framework can be imported
    if python3 -c "import sys; sys.path.append('tests'); import ai_testing_framework" 2>/dev/null; then
        echo "✅ AI testing framework can be imported"
    else
        echo "⚠️  AI testing framework import issues"
    fi
else
    echo "❌ AI testing framework not found"
fi

# Test 4: Quick test run
echo ""
echo "Test 4: Running quick test verification..."

# Create reports directory
mkdir -p reports/test-verification

# Run a simple test discovery to verify setup
echo "Running pytest discovery check..."
if python3 -m pytest --collect-only --tb=no > reports/test-verification/discovery.log 2>&1; then
    echo "✅ Test discovery successful"
else
    echo "⚠️  Test discovery had issues - check reports/test-verification/discovery.log"
fi

# Test 5: TypeScript tests
if [ "$HAS_NODE" = true ]; then
    echo ""
    echo "Test 5: Checking TypeScript test setup..."
    
    # Check vercel-ai-sdk tests
    if [ -d "mem0/vercel-ai-sdk" ] && [ -f "mem0/vercel-ai-sdk/package.json" ]; then
        echo "✅ vercel-ai-sdk test directory found"
        cd mem0/vercel-ai-sdk
        if npm ls jest > /dev/null 2>&1; then
            echo "✅ Jest testing framework available"
        else
            echo "⚠️  Jest not installed - run: cd mem0/vercel-ai-sdk && npm install"
        fi
        cd - > /dev/null
    fi
    
    # Check mem0-ts tests
    if [ -d "mem0/mem0-ts" ] && [ -f "mem0/mem0-ts/package.json" ]; then
        echo "✅ mem0-ts test directory found"
    fi
fi

# Test 6: Check Makefile integration
echo ""
echo "Test 6: Checking Makefile test commands..."
if [ -f "Makefile" ]; then
    if grep -q "test:" Makefile; then
        echo "✅ Makefile test commands found"
        echo "Available test commands:"
        grep "^test" Makefile | head -5 | sed 's/^/  /'
    else
        echo "⚠️  No test commands found in Makefile"
    fi
else
    echo "❌ Makefile not found"
fi

# Summary
echo ""
echo "📊 Verification Summary"
echo "======================"

# Count issues
ISSUES=0
if ! command -v python3 &> /dev/null; then ((ISSUES++)); fi
if [ ! -f "tests/ai_testing_framework.py" ]; then ((ISSUES++)); fi
if [ ! -f "pyproject.toml" ]; then ((ISSUES++)); fi

if [ $ISSUES -eq 0 ]; then
    echo "🎉 All core components verified successfully!"
    echo ""
    echo "🚀 Ready for automation with Cursor BugBot!"
    echo ""
    echo "Quick start commands:"
    echo "  make test-fast     # Fast unit tests"
    echo "  make test          # Full test suite with coverage"
    echo "  make test-smoke    # Basic functionality verification"
    echo "  make check-all     # Quality checks + tests"
else
    echo "⚠️  Found $ISSUES issues that should be addressed"
    echo ""
    echo "Recommended fixes:"
    if ! command -v python3 &> /dev/null; then
        echo "  - Install Python 3"
    fi
    if [ ! -f "tests/ai_testing_framework.py" ]; then
        echo "  - Verify AI testing framework location"
    fi
    if [ ! -f "pyproject.toml" ]; then
        echo "  - Create pyproject.toml configuration"
    fi
fi

echo ""
echo "📝 Detailed logs saved to: reports/test-verification/" 
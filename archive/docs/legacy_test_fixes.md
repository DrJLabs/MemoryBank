# Legacy Test Suite Fixes

## Issue 1: Path Resolution Fix

**File**: `tests/integration/test_integration_simple.py`
**Line 12**: Change path calculation

```python
# BEFORE (broken)
memory_file_path = os.path.join(os.path.dirname(__file__), 'mem0', 'mem0', 'memory', 'main.py')

# AFTER (fixed) 
memory_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'mem0', 'mem0', 'memory', 'main.py')
```

**Apply to all integration tests** with similar path issues.

## Issue 2: mem0 Import Fix

**Solution A**: Add to Python path in test files
```python
# Add at top of test files
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mem0'))
import mem0
```

**Solution B**: Run tests with proper PYTHONPATH
```bash
PYTHONPATH=./mem0:$PYTHONPATH python3 -m pytest tests/
```

**Solution C**: Create setup.py or use proper package installation
```bash
cd mem0 && pip install -e .
```

## Issue 3: pytest Configuration Fix

**File**: `pytest.ini`
**Line 35**: Fix asyncio configuration

```ini
# OPTION 1: Remove problematic line
# asyncio_mode = auto

# OPTION 2: Install plugin and keep
# pip install pytest-asyncio
asyncio_mode = auto

# OPTION 3: Use alternative configuration
addopts = 
    --strict-markers
    --verbose
    --tb=short
    --maxfail=3
    --asyncio-mode=auto
```

## Implementation Priority

1. **High**: Fix path resolution (breaks integration tests)
2. **High**: Fix mem0 imports (breaks all mem0-dependent tests)  
3. **Low**: Fix pytest warning (cosmetic, doesn't break functionality)

## Test Commands After Fixes

```bash
# Test specific integration
python3 -m pytest tests/integration/test_integration_simple.py -v

# Test with mem0 imports
PYTHONPATH=./mem0:$PYTHONPATH python3 -m pytest tests/ -v

# Test pytest configuration
python3 -m pytest --version
``` 
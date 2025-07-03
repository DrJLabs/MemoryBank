"""
BMAD Testing Configuration and Fixtures
Phase 1: Foundation Testing Infrastructure
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock

import pytest

# Add project root to path for BMAD imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import BMAD test configuration
from tests.bmad import BMAD_TEST_CONFIG


# ==================== BMAD AGENT TESTING FIXTURES ====================

@pytest.fixture
def bmad_agent_context():
    """Mock BMAD agent context for testing agent behaviors."""
    return {
        "agent_id": "test_agent",
        "persona": "test_persona",
        "commands": ["*help", "*test", "*status"],
        "memory_enabled": True,
        "context_threshold": 0.7,
    }


@pytest.fixture
def mock_agent_orchestrator():
    """Mock BMAD orchestrator for testing agent transformations."""
    orchestrator = Mock()
    orchestrator.transform_agent = Mock(return_value={"status": "success", "agent": "dev"})
    orchestrator.execute_command = Mock(return_value={"status": "executed", "response": "test response"})
    orchestrator.get_agent_status = Mock(return_value={"active": True, "agent": "test_agent"})
    return orchestrator


@pytest.fixture
def agent_test_scenarios():
    """Test scenarios for agent behavior validation."""
    return [
        {
            "name": "help_command",
            "input": "*help",
            "expected_output": {"type": "help", "commands": list},
            "persona_check": True,
        },
        {
            "name": "invalid_command",
            "input": "invalid_command",
            "expected_output": {"type": "error", "message": str},
            "persona_check": False,
        },
        {
            "name": "agent_transformation",
            "input": "*agent dev",
            "expected_output": {"type": "transformation", "target_agent": "dev"},
            "persona_check": True,
        },
    ]


# ==================== MEMORY SYSTEM TESTING FIXTURES ====================

@pytest.fixture
def mock_memory_system():
    """Mock memory system for testing memory operations."""
    memory_system = Mock()

    # Mock memory operations
    memory_system.add = Mock(return_value={"id": "test_memory_123", "success": True})
    memory_system.search = Mock(return_value=[
        {"id": "mem_1", "content": "test memory", "confidence": 0.95},
        {"id": "mem_2", "content": "another memory", "confidence": 0.87},
    ])
    memory_system.get_context = Mock(return_value={
        "relevant_memories": ["mem_1", "mem_2"],
        "confidence": 0.9,
        "categories": ["TECHNICAL", "WORKFLOW"],
    })
    memory_system.categorize = Mock(return_value="TECHNICAL")

    return memory_system


@pytest.fixture
def memory_test_data():
    """Test data for memory operations testing."""
    return {
        "valid_memories": [
            {
                "content": "User prefers Python for AI development",
                "expected_category": "PREFERENCE",
                "metadata": {"user_id": "test_user", "confidence": 0.95},
            },
            {
                "content": "BMAD agent transformation completed successfully",
                "expected_category": "WORKFLOW",
                "metadata": {"agent": "orchestrator", "confidence": 0.92},
            },
            {
                "content": "Testing framework uses pytest with coverage reporting",
                "expected_category": "TECHNICAL",
                "metadata": {"component": "testing", "confidence": 0.98},
            },
        ],
        "invalid_memories": [
            {"content": "", "reason": "empty_content"},
            {"content": None, "reason": "null_content"},
            {"content": "x" * 10000, "reason": "too_long"},
        ],
    }


@pytest.fixture
def memory_property_strategies():
    """Mock property-based testing strategies for memory operations."""
    class MockStrategies:
        @staticmethod
        def text(min_size=1, max_size=1000):
            return lambda: f"test_memory_content_{int(time.time())}"

        @staticmethod
        def sampled_from(choices):
            return lambda: choices[0] if choices else "TECHNICAL"

        @staticmethod
        def dictionaries(keys=None, values=None, min_size=0, max_size=10):
            return lambda: {"test_key": "test_value", "timestamp": time.time()}

        @staticmethod
        def floats(min_value=0.0, max_value=1.0):
            return lambda: 0.85

    return MockStrategies()


# ==================== WORKFLOW TESTING FIXTURES ====================

@pytest.fixture
def workflow_test_config():
    """Configuration for workflow testing."""
    return {
        "workflows": [
            "greenfield-fullstack",
            "brownfield-service",
            "greenfield-ui",
            "brownfield-fullstack",
        ],
        "agents": ["pm", "dev", "architect", "qa"],
        "stages": ["requirements", "design", "implementation", "testing", "review"],
        "success_criteria": {
            "stage_completion": 0.98,
            "agent_handoff": 0.99,
            "artifact_quality": 0.95,
        },
    }


@pytest.fixture
def mock_workflow_orchestrator():
    """Mock workflow orchestrator for testing workflow execution."""
    orchestrator = Mock()
    orchestrator.start_workflow = Mock(return_value={"id": "workflow_123", "status": "started"})
    orchestrator.get_workflow_status = Mock(return_value={"status": "in_progress", "stage": "implementation"})
    orchestrator.complete_stage = Mock(return_value={"status": "completed", "next_stage": "testing"})
    orchestrator.handoff_to_agent = Mock(return_value={"status": "handoff_success", "agent": "dev"})
    return orchestrator


# ==================== QUALITY GATES TESTING FIXTURES ====================

@pytest.fixture
def quality_metrics_tracker():
    """Track quality metrics during testing."""
    metrics = {
        "test_start_time": time.time(),
        "coverage_percentage": 0.0,
        "performance_ms": [],
        "memory_accuracy": [],
        "agent_persona_scores": [],
        "workflow_success_rate": 0.0,
    }

    yield metrics

    # Calculate final metrics
    metrics["test_duration"] = time.time() - metrics["test_start_time"]
    metrics["avg_performance"] = sum(metrics["performance_ms"]) / len(metrics["performance_ms"]) if metrics["performance_ms"] else 0
    metrics["avg_memory_accuracy"] = sum(metrics["memory_accuracy"]) / len(metrics["memory_accuracy"]) if metrics["memory_accuracy"] else 0


@pytest.fixture
def quality_gate_validator():
    """Validator for quality gates."""
    def validate_quality_gates(metrics: Dict[str, Any]) -> Dict[str, bool]:
        return {
            "coverage_gate": metrics.get("coverage_percentage", 0) >= BMAD_TEST_CONFIG["coverage_threshold"],
            "performance_gate": metrics.get("avg_performance", float('inf')) <= BMAD_TEST_CONFIG["performance_threshold_ms"],
            "memory_accuracy_gate": metrics.get("avg_memory_accuracy", 0) >= BMAD_TEST_CONFIG["memory_accuracy_threshold"],
            "agent_persona_gate": all(score >= BMAD_TEST_CONFIG["agent_persona_threshold"] for score in metrics.get("agent_persona_scores", [1.0])),
            "workflow_success_gate": metrics.get("workflow_success_rate", 0) >= BMAD_TEST_CONFIG["workflow_success_threshold"],
        }

    return validate_quality_gates


# ==================== PERFORMANCE TESTING FIXTURES ====================

@pytest.fixture
def performance_monitor():
    """Monitor performance during tests."""
    import psutil
    import threading

    process = psutil.Process()
    start_time = time.time()
    start_memory = process.memory_info().rss

    # Performance data collection with dynamic duration calculation
    class PerformanceData:
        def __init__(self, start_time, start_memory, process):
            self.start_time = start_time
            self.start_memory = start_memory
            self.process = process
            self.cpu_samples = []
            self.memory_samples = []
            self.end_time = None
            self.end_memory = None

        def __getitem__(self, key):
            if key == "duration":
                current_time = time.time()
                return current_time - self.start_time
            elif key == "memory_delta":
                current_memory = self.process.memory_info().rss
                return current_memory - self.start_memory
            elif key == "avg_cpu":
                return sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0
            elif key == "peak_memory":
                return max(self.memory_samples) if self.memory_samples else self.start_memory
            elif key == "start_time":
                return self.start_time
            elif key == "start_memory":
                return self.start_memory
            elif key == "cpu_samples":
                return self.cpu_samples
            elif key == "memory_samples":
                return self.memory_samples
            else:
                raise KeyError(f"Unknown performance metric: {key}")

        def get(self, key, default=None):
            try:
                return self[key]
            except KeyError:
                return default

    performance_data = PerformanceData(start_time, start_memory, process)

    # Start monitoring thread
    monitoring = True

    def monitor():
        while monitoring:
            try:
                performance_data.cpu_samples.append(process.cpu_percent())
                performance_data.memory_samples.append(process.memory_info().rss)
                time.sleep(0.1)
            except:
                break

    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()

    yield performance_data

    # Stop monitoring
    monitoring = False
    performance_data.end_time = time.time()
    performance_data.end_memory = process.memory_info().rss


# ==================== BMAD INTEGRATION FIXTURES ====================

@pytest.fixture
def bmad_core_config():
    """Load BMAD core configuration for testing."""
    config_path = PROJECT_ROOT / ".bmad-core" / "core-config.yml"
    if config_path.exists():
        try:
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except ImportError:
            # Mock YAML parsing if PyYAML not available
            return {
                "memoryBank": {"enabled": True, "confidenceThreshold": 0.7},
                "devLoadAlwaysFiles": ["docs/architecture.md"],
                "agentMemoryConfig": {"mandatoryContext": True},
            }
    return {}


@pytest.fixture
def mock_ai_commands():
    """Mock AI memory commands for testing."""
    commands = Mock()
    commands.get_context = Mock(return_value={
        "memories": ["memory1", "memory2"],
        "confidence": 0.85,
        "categories": ["TECHNICAL", "WORKFLOW"],
    })
    commands.add_smart = Mock(return_value={"success": True, "id": "memory_new"})
    commands.search = Mock(return_value={"results": [], "count": 0})
    return commands


# ==================== AUTOUSE FIXTURES FOR BMAD ====================

@pytest.fixture(autouse=True)
def bmad_test_setup():
    """Automatically set up BMAD testing environment."""
    # Create necessary directories
    test_dirs = [
        "reports/bmad",
        "logs/bmad",
        ".ai/bmad",
    ]

    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    # Set BMAD testing environment variables
    os.environ["BMAD_TEST_MODE"] = "true"
    os.environ["BMAD_TEST_PHASE"] = "1"

    yield

    # Cleanup
    os.environ.pop("BMAD_TEST_MODE", None)
    os.environ.pop("BMAD_TEST_PHASE", None)


# ==================== PYTEST HOOKS FOR BMAD ====================

def pytest_runtest_setup(item):
    """Setup for each BMAD test."""
    if "bmad" in item.nodeid:
        # Mark all BMAD tests
        item.add_marker(pytest.mark.bmad)

        # Add performance monitoring to slow tests
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.performance)


def pytest_runtest_teardown(item, nextitem):
    """Teardown for each BMAD test."""
    if "bmad" in item.nodeid and hasattr(item, "_performance_data"):
        # Log performance data for slow tests
        duration = getattr(item, "_duration", 0)
        if duration > 1.0:
            print(f"\n⚠️ BMAD Slow Test: {item.name} took {duration:.2f}s")


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Custom terminal summary for BMAD tests."""
    if hasattr(terminalreporter, 'stats'):
        bmad_tests = [test for test in terminalreporter.stats.get('passed', []) + terminalreporter.stats.get('failed', []) if 'bmad' in str(test)]

        if bmad_tests:
            terminalreporter.write_sep("=", "BMAD Testing Summary")
            terminalreporter.write_line(f"🔬 BMAD Tests Run: {len(bmad_tests)}")
            terminalreporter.write_line("🎯 Phase 1: Foundation Testing")
            terminalreporter.write_line(f"📊 Quality Threshold: {BMAD_TEST_CONFIG['coverage_threshold']}% coverage")
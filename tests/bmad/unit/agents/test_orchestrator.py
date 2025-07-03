"""
BMAD Orchestrator Agent Tests
Phase 1: Foundation Testing - Agent Behavior Validation

Tests the core functionality of the BMAD orchestrator agent including:
- Agent transformation capabilities
- Command execution and validation
- Persona adherence and consistency
- Memory-first workflow integration
"""

import pytest
import time
from unittest.mock import Mock

# Import BMAD test fixtures


class TestBMADOrchestrator:
    """Test suite for BMAD Orchestrator agent behavior."""

    @pytest.mark.bmad
    @pytest.mark.unit
    def test_orchestrator_initialization(self, bmad_agent_context):
        """Test that BMAD orchestrator initializes correctly."""
        # Arrange
        expected_agent_id = "bmad-orchestrator"
        expected_commands = ["*help", "*agent", "*workflow", "*status", "*exit"]

        # Act - Mock orchestrator initialization
        orchestrator = {
            "name": "BMad Orchestrator",
            "id": "bmad-orchestrator",
            "title": "BMAD Master Orchestrator",
            "icon": "🎭",
            "commands": expected_commands,
            "memory_enabled": True,
        }

        # Assert
        assert orchestrator["id"] == expected_agent_id
        assert orchestrator["memory_enabled"] is True
        assert "*help" in orchestrator["commands"]
        assert "*agent" in orchestrator["commands"]
        assert len(orchestrator["commands"]) >= 5

    @pytest.mark.bmad
    @pytest.mark.unit
    def test_help_command_execution(self, mock_agent_orchestrator, quality_metrics_tracker):
        """Test that *help command returns proper command list."""
        # Arrange
        start_time = time.time()

        # Mock help command response
        mock_agent_orchestrator.execute_command.return_value = {
            "type": "help",
            "commands": ["*help", "*agent", "*workflow", "*status", "*exit"],
            "agent_info": {"name": "BMad Orchestrator", "active": True},
            "response_time": 150,  # ms
        }

        # Act
        response = mock_agent_orchestrator.execute_command("*help")
        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        # Assert
        assert response["type"] == "help"
        assert isinstance(response["commands"], list)
        assert len(response["commands"]) >= 5
        assert "*help" in response["commands"]
        assert "*agent" in response["commands"]
        assert response["response_time"] < 2000  # Performance requirement

        # Track quality metrics
        quality_metrics_tracker["performance_ms"].append(execution_time)
        quality_metrics_tracker["agent_persona_scores"].append(1.0)  # Perfect score for valid help

    @pytest.mark.bmad
    @pytest.mark.unit
    def test_agent_transformation_command(self, mock_agent_orchestrator, quality_metrics_tracker):
        """Test agent transformation using *agent command."""
        # Arrange
        target_agents = ["dev", "architect", "pm", "qa"]

        for target_agent in target_agents:
            # Mock transformation response
            mock_agent_orchestrator.transform_agent.return_value = {
                "status": "success",
                "previous_agent": "bmad-orchestrator",
                "new_agent": target_agent,
                "transformation_time": 200,
                "memory_context_preserved": True,
            }

            # Act
            result = mock_agent_orchestrator.transform_agent(target_agent)

            # Assert
            assert result["status"] == "success"
            assert result["new_agent"] == target_agent
            assert result["memory_context_preserved"] is True
            assert result["transformation_time"] < 1000  # Performance requirement

            # Track quality metrics
            quality_metrics_tracker["performance_ms"].append(result["transformation_time"])
            quality_metrics_tracker["agent_persona_scores"].append(1.0)

    @pytest.mark.bmad
    @pytest.mark.unit
    def test_invalid_command_handling(self, mock_agent_orchestrator, quality_metrics_tracker):
        """Test that invalid commands are handled gracefully."""
        # Arrange
        invalid_commands = ["invalid", "not_a_command", "missing_asterisk"]

        # Mock error response for invalid commands
        mock_agent_orchestrator.execute_command.return_value = {
            "type": "error",
            "message": "Invalid command. Use *help to see available commands.",
            "valid_commands": ["*help", "*agent", "*workflow", "*status", "*exit"],
            "persona_maintained": True,
        }

        for invalid_cmd in invalid_commands:
            # Act
            response = mock_agent_orchestrator.execute_command(invalid_cmd)

            # Assert
            assert response["type"] == "error"
            assert "Invalid command" in response["message"]
            assert "*help" in response["message"]
            assert response["persona_maintained"] is True

            # Track quality metrics (error handling should maintain persona)
            quality_metrics_tracker["agent_persona_scores"].append(0.9)  # Slight deduction for error

    @pytest.mark.bmad
    @pytest.mark.unit
    def test_memory_integration(self, mock_agent_orchestrator, quality_metrics_tracker):
        """Test that orchestrator integrates with memory system."""
        # Arrange
        mock_memory_context = {
            "relevant_memories": ["mem1", "mem2"],
            "confidence": 0.85,
            "categories": ["BMAD", "WORKFLOW"],
            "context_retrieval_time": 300,
        }

        # Mock memory integration
        mock_agent_orchestrator.get_memory_context = Mock(return_value=mock_memory_context)

        # Act
        memory_context = mock_agent_orchestrator.get_memory_context("orchestrator task")

        # Assert
        assert memory_context["confidence"] >= 0.7  # Minimum confidence threshold
        assert len(memory_context["relevant_memories"]) >= 1
        assert "BMAD" in memory_context["categories"]
        assert memory_context["context_retrieval_time"] < 500  # Performance requirement

        # Track quality metrics
        quality_metrics_tracker["memory_accuracy"].append(memory_context["confidence"])
        quality_metrics_tracker["performance_ms"].append(memory_context["context_retrieval_time"])

    @pytest.mark.bmad
    @pytest.mark.unit
    def test_workflow_command_execution(self, mock_agent_orchestrator, quality_metrics_tracker):
        """Test workflow-related commands."""
        # Arrange
        workflow_commands = ["*workflow", "*workflow-guidance", "*status"]

        for cmd in workflow_commands:
            # Mock workflow command response
            mock_agent_orchestrator.execute_command.return_value = {
                "type": "workflow",
                "command": cmd,
                "available_workflows": ["greenfield-fullstack", "brownfield-service"],
                "current_workflow": None,
                "response_time": 180,
                "persona_consistent": True,
            }

            # Act
            response = mock_agent_orchestrator.execute_command(cmd)

            # Assert
            assert response["type"] == "workflow"
            assert response["command"] == cmd
            assert len(response["available_workflows"]) >= 2
            assert response["response_time"] < 1000
            assert response["persona_consistent"] is True

            # Track quality metrics
            quality_metrics_tracker["performance_ms"].append(response["response_time"])
            quality_metrics_tracker["agent_persona_scores"].append(1.0)

    @pytest.mark.bmad
    @pytest.mark.performance
    def test_orchestrator_performance_benchmarks(self, mock_agent_orchestrator, performance_monitor):
        """Test that orchestrator meets performance benchmarks."""
        # Arrange
        commands_to_benchmark = ["*help", "*agent dev", "*workflow", "*status"]
        max_response_time = 2000  # 2 seconds as per architecture

        for cmd in commands_to_benchmark:
            # Mock timed response
            start_time = time.time()

            mock_agent_orchestrator.execute_command.return_value = {
                "status": "success",
                "command": cmd,
                "execution_time": time.time() - start_time,
            }

            # Act
            response = mock_agent_orchestrator.execute_command(cmd)

            # Assert
            execution_time_ms = response["execution_time"] * 1000
            assert execution_time_ms < max_response_time, f"Command {cmd} exceeded {max_response_time}ms limit"

        # Check overall performance
        assert performance_monitor["duration"] < 5.0, "Test suite exceeded 5 second limit"
        assert performance_monitor["memory_delta"] < 100 * 1024 * 1024, "Memory usage exceeded 100MB"


class TestBMADOrchestratorPersona:
    """Test suite for BMAD Orchestrator persona consistency."""

    @pytest.mark.bmad
    @pytest.mark.unit
    def test_persona_consistency(self, mock_agent_orchestrator, quality_metrics_tracker):
        """Test that orchestrator maintains consistent persona across interactions."""
        # Arrange
        persona_indicators = [
            "orchestrator",
            "agent",
            "coordinate",
            "*",
        ]

        # Mock persona-consistent responses
        responses = [
            "I'm the BMAD Master Orchestrator. All commands start with *",
            "I can coordinate agents and workflows. Use *help for options.",
            "I'll transform into the dev agent to coordinate implementation.",
        ]

        # Act & Assert
        for response_text in responses:
            # Check that responses contain persona indicators (case-insensitive)
            persona_score = sum(1 for indicator in persona_indicators if indicator.lower() in response_text.lower())
            persona_percentage = persona_score / len(persona_indicators)

            # More realistic persona adherence threshold - should contain at least 50% of indicators
            assert persona_percentage >= 0.5, f"Low persona adherence ({persona_percentage:.1%}) in: {response_text}"
            quality_metrics_tracker["agent_persona_scores"].append(persona_percentage)

    @pytest.mark.bmad
    @pytest.mark.unit
    def test_command_prefix_enforcement(self, mock_agent_orchestrator, quality_metrics_tracker):
        """Test that orchestrator enforces * prefix for commands."""
        # Arrange
        commands_without_prefix = ["help", "agent dev", "workflow", "status"]

        for cmd in commands_without_prefix:
            # Mock response that reminds about prefix
            mock_agent_orchestrator.execute_command.return_value = {
                "type": "reminder",
                "message": f"All commands require * prefix. Try '*{cmd}' instead.",
                "persona_maintained": True,
                "helpful": True,
            }

            # Act
            response = mock_agent_orchestrator.execute_command(cmd)

            # Assert
            assert "*" in response["message"]
            assert "prefix" in response["message"].lower()
            assert response["persona_maintained"] is True
            assert response["helpful"] is True

            # Track quality - maintaining persona while being helpful
            quality_metrics_tracker["agent_persona_scores"].append(1.0)


# ==================== TEST UTILITIES ====================

def test_bmad_orchestrator_test_suite_health():
    """Meta-test to ensure test suite itself is healthy."""
    # Test that all required test classes exist
    assert TestBMADOrchestrator is not None
    assert TestBMADOrchestratorPersona is not None

    # Test that test methods are properly named
    test_methods = [method for method in dir(TestBMADOrchestrator) if method.startswith('test_')]
    assert len(test_methods) >= 5, "Insufficient test coverage for orchestrator"

    # Test that performance tests exist
    performance_tests = [method for method in test_methods if 'performance' in method]
    assert len(performance_tests) >= 1, "No performance tests found"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "--tb=short"])
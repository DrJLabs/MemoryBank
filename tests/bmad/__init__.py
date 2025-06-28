"""
BMAD Testing & Quality Framework
Phase 1: Foundation Testing Infrastructure

This module provides comprehensive testing for the BMAD (Brownfield Memory-Augmented Development) 
foundation including agent behavior validation, memory system testing, and workflow integration.
"""

__version__ = "1.0.0"
__author__ = "BMAD Development Team"

# Testing configuration
BMAD_TEST_CONFIG = {
    "coverage_threshold": 95,
    "performance_threshold_ms": 2000,
    "memory_accuracy_threshold": 0.99,
    "agent_persona_threshold": 0.95,
    "workflow_success_threshold": 0.98,
}

# Test categories for BMAD
BMAD_TEST_CATEGORIES = [
    "agent_behavior",
    "memory_operations", 
    "workflow_integration",
    "quality_gates",
    "performance",
    "security",
]

# Export key components
__all__ = [
    "BMAD_TEST_CONFIG",
    "BMAD_TEST_CATEGORIES",
] 
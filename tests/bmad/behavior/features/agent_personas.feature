Feature: BMAD Agent Persona Behavior Validation
  As a BMAD system user
  I want agents to maintain consistent personas
  So that I have predictable and reliable agent interactions

  Background:
    Given the BMAD system is initialized
    And the memory system is available
    And all agents are configured with their personas

  Scenario: Orchestrator Agent Maintains Master Orchestrator Persona
    Given I am interacting with the "bmad-orchestrator" agent
    When I send the command "*help"
    Then the agent should respond as the "BMAD Master Orchestrator"
    And the response should mention "commands start with *"
    And the response should include available agents and workflows
    And the persona consistency score should be >= 95%

  Scenario: Orchestrator Agent Enforces Command Prefix
    Given I am interacting with the "bmad-orchestrator" agent
    When I send a command without the "*" prefix like "help"
    Then the agent should remind me about the "*" prefix requirement
    And the agent should maintain its helpful persona
    And the agent should suggest the correct command format
    And the persona consistency score should be >= 95%

  Scenario: Agent Transformation Preserves Context
    Given I am interacting with the "bmad-orchestrator" agent
    And there is existing memory context about "testing implementation"
    When I execute the command "*agent dev"
    Then the agent should transform to the "dev" agent
    And the memory context should be preserved
    And the new agent should acknowledge the transformation
    And the context retrieval should be successful

  Scenario: Dev Agent Maintains Technical Persona
    Given I am interacting with the "dev" agent
    When I ask about implementing unit tests
    Then the agent should respond as "James" the Full Stack Developer
    And the response should be technically focused and concise
    And the agent should mention memory-first development workflow
    And the persona consistency score should be >= 95%

  Scenario: Agent Memory Integration Workflow
    Given I am interacting with any BMAD agent
    When I start a development task
    Then the agent should retrieve relevant memory context first
    And the agent should apply stored development patterns
    And the agent should store new learnings after task completion
    And the memory accuracy should be >= 99%

  Scenario Outline: Multiple Agent Persona Consistency
    Given I am interacting with the "<agent_id>" agent
    When I interact with the agent for "<interaction_count>" interactions
    Then the agent should maintain persona consistency across all interactions
    And each response should align with the "<expected_persona>" characteristics
    And the average persona score should be >= 95%

    Examples:
      | agent_id         | expected_persona           | interaction_count |
      | bmad-orchestrator| Master Orchestrator        | 5                 |
      | dev              | Full Stack Developer       | 5                 |
      | architect        | System Architect           | 3                 |
      | pm               | Product Manager            | 3                 |

  Scenario: Cross-Agent Communication Preserves Context
    Given I start with the "bmad-orchestrator" agent
    And I have established context about "testing architecture"
    When I transform to the "architect" agent via "*agent architect"
    And then transform to the "dev" agent via "*agent dev"
    Then each agent should receive the previous context
    And the context should be enriched by each agent interaction
    And no context should be lost during transformations
    And the final context accuracy should be >= 98%

  Scenario: Agent Error Handling Maintains Persona
    Given I am interacting with any BMAD agent
    When I provide invalid input or malformed commands
    Then the agent should handle errors gracefully
    And the agent should maintain its persona while providing help
    And the agent should offer constructive guidance
    And the persona consistency should remain >= 90% even during errors

  Scenario: Agent Performance Under Load
    Given I am interacting with the "bmad-orchestrator" agent
    When I send 10 rapid commands within 5 seconds
    Then each response should maintain persona consistency
    And all responses should be delivered within 2 seconds
    And the agent should handle concurrent requests gracefully
    And the system should maintain >= 95% reliability 
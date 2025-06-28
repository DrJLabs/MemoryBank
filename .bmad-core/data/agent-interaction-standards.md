# BMAD Agent Interaction Standards

**Version**: 1.0 (Foundational Release)  
**Status**: Agent Collaboration Framework  
**Created**: 2025-06-28  
**Purpose**: Formal standards for cross-agent collaboration, handoffs, and workflow state management

---

## 🎯 **OVERVIEW**

BMAD agent interactions require **systematic coordination** to maintain workflow continuity, context preservation, and quality standards across agent transitions. This document defines the formal protocols for seamless agent collaboration.

### Core Interaction Principles

1. **Context Preservation**: Complete state transfer across agent transitions
2. **Memory Continuity**: Shared learning and insights across agents  
3. **Quality Consistency**: Maintained standards throughout workflow progression
4. **Explicit Handoffs**: Clear communication of responsibilities and deliverables
5. **State Transparency**: Visible workflow progress and current status

---

## 🔄 **AGENT HANDOFF PROTOCOLS**

### Standard Handoff Procedure

Every agent transition must follow this **5-phase handoff protocol**:

#### Phase 1: Pre-Handoff Context Preparation
**Outgoing Agent Responsibilities:**
1. **Complete Current Tasks**: Ensure all active work reaches stable checkpoint
2. **Gather Handoff Context**: Compile artifacts, decisions, and constraints
3. **Store Insights**: Execute `ai-add-smart` with key learnings and patterns
4. **Validate Deliverables**: Confirm all outputs meet quality standards
5. **Prepare Transition Summary**: Create concise handoff documentation

**Required Information Package:**
- **Completed Artifacts**: All deliverables created during agent session
- **Active Context**: Current project state, requirements, and constraints  
- **Decision History**: Key decisions made and rationale
- **Quality Status**: Validation results and any outstanding issues
- **Next Steps**: Recommended actions for incoming agent

#### Phase 2: Orchestrator Coordination
**BMAD Orchestrator Responsibilities:**
1. **Validate Readiness**: Confirm outgoing agent completion and deliverable quality
2. **Select Next Agent**: Choose optimal agent based on workflow stage and memory patterns
3. **Prepare Context Package**: Aggregate all relevant artifacts and context
4. **Announce Transition**: Clear communication of agent change and handoff
5. **Initiate Next Agent**: Transform with full context and handoff package

#### Phase 3: Incoming Agent Activation
**Incoming Agent Startup Protocol:**
1. **Identity Declaration**: Announce name, role, and capabilities
2. **Enhanced Integration**: Execute Infisical and memory system integration
3. **Context Retrieval**: Load relevant context using `ai-get-context` and `ai-ctx-*` commands
4. **Handoff Review**: Acknowledge received artifacts and validate context understanding
5. **Next Steps Confirmation**: Confirm understanding of expected deliverables and approach

#### Phase 4: Context Validation
**Mutual Validation Requirements:**
1. **Artifact Verification**: Incoming agent confirms access to all required deliverables
2. **Context Understanding**: Demonstrate comprehension of project state and requirements
3. **Quality Continuity**: Commit to maintaining established quality standards
4. **Scope Confirmation**: Verify understanding of role boundaries and responsibilities
5. **Issue Escalation**: Identify any gaps or concerns requiring orchestrator attention

#### Phase 5: Workflow Continuation
**Smooth Transition Execution:**
1. **Status Update**: Update workflow state with new agent and current stage
2. **Memory Integration**: Load agent-specific context and successful patterns
3. **Task Initiation**: Begin first task with full context awareness
4. **Progress Tracking**: Establish clear progress indicators and checkpoints
5. **Continuous Communication**: Maintain transparency with user and orchestrator

### Handoff Documentation Template

```markdown
## AGENT HANDOFF SUMMARY

**From:** [Outgoing Agent Name] ([Agent ID])
**To:** [Incoming Agent Name] ([Agent ID])  
**Transition Date:** [YYYY-MM-DD HH:MM]
**Workflow Stage:** [Current stage]

### Completed Work
- ✅ [Artifact 1]: [Brief description and quality status]
- ✅ [Artifact 2]: [Brief description and quality status]
- ✅ [Key Decision]: [Decision made and rationale]

### Context Package
- **Project Status**: [Current state summary]
- **Active Requirements**: [Key requirements and constraints]
- **Quality Standards**: [Established standards and validation results]
- **Technical Context**: [Technology stack, architecture decisions]

### Recommendations for Next Agent
1. **Priority Actions**: [Most important next steps]
2. **Key Considerations**: [Important factors to remember]
3. **Potential Challenges**: [Known issues or concerns]
4. **Success Criteria**: [How to measure successful completion]

### Memory Insights Stored
- [Key patterns or learnings stored using ai-add-smart]
- [Successful approaches that should be repeated]
- [Approaches to avoid or modify]

**Handoff Status**: ✅ COMPLETE / ⚠️ PARTIAL / ❌ ISSUES
**Next Agent Confirmation**: [Incoming agent acknowledgment]
```

---

## 🧠 **MEMORY INTEGRATION STANDARDS**

### Cross-Agent Memory Sharing

**Memory Categories for Agent Collaboration:**
- `WORKFLOW`: Process patterns, successful orchestrations, handoff experiences
- `TECHNICAL`: Implementation approaches, tool choices, technical decisions
- `PROJECT`: Project-specific context, requirements evolution, constraint changes
- `QUALITY`: Standards applied, validation approaches, issue resolution patterns
- `COLLABORATION`: Agent interaction patterns, effective handoff strategies

### Pre-Agent Memory Protocol

**Required Context Loading (MANDATORY):**
```bash
# Load general context for task
ai-get-context "{task_description}" [type]

# Load technical context for agent role
ai-ctx-tech "{agent_domain_expertise}"

# Load project-specific context
ai-ctx-project "{current_project_phase}"

# Load workflow context
ai-ctx-workflow "{current_workflow_stage}"

# Load collaboration patterns
ai-ctx-workflow "agent {previous_agent} to {current_agent} handoff"
```

### Post-Agent Memory Protocol

**Required Learning Storage (MANDATORY):**
```bash
# Store agent-specific learnings
ai-add-smart "AGENT {agent_id}: {task_type} - Approach: {method} - Result: {outcome} - Insight: {lesson}"

# Store collaboration patterns
ai-add-smart "HANDOFF: {from_agent} → {to_agent} - Context: {handoff_context} - Effectiveness: {rating} - Improvement: {suggestion}"

# Store workflow insights
ai-add-smart "WORKFLOW: {workflow_stage} - Agent: {agent_id} - Success Factors: {factors} - Lessons: {insights}"

# Store quality patterns
ai-add-smart "QUALITY: {validation_type} - Standards: {applied_standards} - Results: {outcomes} - Patterns: {reusable_approaches}"
```

### Memory-Driven Decision Making

**Agent Selection Enhancement:**
- **Context Check**: `ai-search "similar {task_type}" WORKFLOW` before agent recommendation
- **Pattern Application**: Use successful handoff patterns from memory for optimal transitions
- **Preference Respect**: Honor user preferences for agent types and collaboration styles stored in memory
- **Continuous Improvement**: Apply lessons learned from previous agent interactions

---

## 📋 **WORKFLOW STATE MANAGEMENT**

### State Preservation Standards

**Required State Information:**
1. **Current Workflow**: Active workflow ID and stage
2. **Completed Stages**: Fully completed workflow phases with artifacts
3. **Active Stage**: Current stage progress and remaining tasks
4. **Next Stage**: Upcoming stage and transition requirements
5. **Context Dependencies**: Cross-stage dependencies and artifact relationships

### Artifact Management Protocol

**Artifact Lifecycle Management:**
- **Creation**: Record artifact creation with agent, timestamp, and purpose
- **Validation**: Track validation status and quality metrics
- **Version Control**: Maintain artifact versions and change history
- **Accessibility**: Ensure availability to relevant agents throughout workflow
- **Archival**: Preserve completed artifacts with full context and relationships

### State Transition Validation

**Transition Readiness Checklist:**
- [ ] All stage deliverables completed and validated
- [ ] Quality standards met and documented
- [ ] Context package prepared and verified
- [ ] Next stage requirements understood
- [ ] Agent capabilities matched to upcoming needs
- [ ] Memory insights stored for future reference

---

## 🤝 **AGENT COLLABORATION PATTERNS**

### Successful Collaboration Models

#### Sequential Agent Pattern
**Use Case**: Linear workflow progression with clear stage boundaries
**Pattern**: Agent A → Orchestrator → Agent B → Orchestrator → Agent C
**Benefits**: Clear handoffs, complete context transfer, quality gates
**Best For**: Greenfield development, structured analysis, systematic implementation

#### Collaborative Agent Pattern  
**Use Case**: Complex tasks requiring multiple perspectives simultaneously
**Pattern**: Agent A + Agent B → Shared Context → Collaborative Deliverable
**Benefits**: Diverse expertise, real-time collaboration, comprehensive solutions
**Best For**: Architecture design, complex problem solving, quality assurance

#### Iterative Agent Pattern
**Use Case**: Refinement-based work requiring multiple cycles
**Pattern**: Agent A → Review → Agent A (refined) → Review → Agent B
**Benefits**: Continuous improvement, quality enhancement, iterative refinement
**Best For**: Document creation, design iteration, solution optimization

### Agent Interaction Protocols

#### Cross-Agent Communication Standards
- **Status Updates**: Regular progress communication through orchestrator
- **Resource Sharing**: Shared access to artifacts and context information
- **Quality Reviews**: Peer validation of deliverables when appropriate
- **Conflict Resolution**: Escalation paths for disagreements or conflicts
- **Learning Exchange**: Knowledge sharing through memory system

#### Collaborative Decision Making
- **Decision Authority**: Clear authority boundaries for each agent role
- **Consultation Protocol**: When to seek input from other agents
- **Consensus Building**: Methods for reaching agreement on complex decisions
- **Documentation Standards**: Recording collaborative decisions and rationale

---

## 🎯 **QUALITY CONTINUITY STANDARDS**

### Quality Consistency Across Agents

**Universal Quality Principles:**
1. **Evidence-Based Outputs**: All deliverables grounded in verifiable information
2. **Systematic Approaches**: Structured methods applied consistently across agents
3. **User-Centric Focus**: Maintained focus on user goals and requirements
4. **Actionable Results**: Clear, implementable outputs with defined success criteria
5. **Continuous Improvement**: Learning integration for quality enhancement

### Quality Validation Points

**Stage-Level Quality Gates:**
- **Input Validation**: Verify quality of artifacts received from previous agent
- **Process Validation**: Confirm adherence to established quality standards
- **Output Validation**: Validate deliverable quality before handoff
- **Integration Validation**: Ensure deliverables integrate properly with existing work
- **User Validation**: Confirm alignment with user goals and expectations

### Quality Metrics and Tracking

**Measurable Quality Indicators:**
- **Completeness**: Percentage of requirements addressed
- **Accuracy**: Factual correctness and data validity
- **Consistency**: Alignment with established standards and patterns
- **Usability**: Practical applicability and actionability
- **Maintainability**: Long-term viability and update capability

---

## 🚀 **IMPLEMENTATION GUIDELINES**

### For Agent Developers

**Agent Design Requirements:**
1. **Startup Protocol Compliance**: Implement standard startup sequence with memory integration
2. **Handoff Capability**: Build in handoff preparation and context transfer capabilities
3. **Memory Integration**: Include pre-task context loading and post-task insight storage
4. **Quality Standards**: Implement validation and quality assurance mechanisms
5. **State Awareness**: Maintain awareness of workflow context and progression

### For Orchestrator Implementation

**Orchestration Enhancement:**
1. **Context Aggregation**: Capability to compile comprehensive handoff packages
2. **Agent Matching**: Memory-driven agent selection based on task requirements and patterns
3. **Quality Monitoring**: Tracking and validation of quality standards across agents
4. **State Management**: Comprehensive workflow state tracking and preservation
5. **Conflict Resolution**: Mechanisms for handling agent coordination issues

### For Workflow Designers

**Workflow Design Considerations:**
1. **Clear Stage Boundaries**: Well-defined transition points between agents
2. **Context Requirements**: Explicit context needs for each stage and agent
3. **Quality Checkpoints**: Built-in validation points and quality gates
4. **Flexibility Points**: Opportunities for workflow adaptation based on context
5. **Rollback Mechanisms**: Ability to return to previous stages if needed

---

## 📚 **APPENDIX: TROUBLESHOOTING GUIDE**

### Common Handoff Issues

**Issue**: Context Loss During Transition
**Symptoms**: Incoming agent lacks key information or understanding
**Resolution**: Validate handoff package completeness, enhance context transfer protocol
**Prevention**: Implement mandatory context validation checkpoint

**Issue**: Quality Standard Inconsistency
**Symptoms**: Deliverable quality varies across agents
**Resolution**: Reinforce quality standards, implement peer review process
**Prevention**: Establish clear quality metrics and validation requirements

**Issue**: Workflow State Confusion
**Symptoms**: Agents unsure of current stage or next steps
**Resolution**: Update workflow state tracking, clarify stage boundaries
**Prevention**: Implement explicit state communication and validation

### Escalation Procedures

**Level 1**: Agent-to-Agent Direct Resolution
- **Scope**: Minor clarifications, simple context questions
- **Process**: Direct communication through orchestrator
- **Timeline**: Immediate resolution expected

**Level 2**: Orchestrator Mediation
- **Scope**: Context conflicts, quality disagreements, role boundary issues
- **Process**: Orchestrator review and guidance
- **Timeline**: Resolution within current session

**Level 3**: User Intervention
- **Scope**: Major workflow changes, significant quality issues, strategic decisions
- **Process**: User consultation and decision
- **Timeline**: May require session pause and resumption

---

**This document establishes the foundation for seamless agent collaboration in the BMAD methodology. All agents and workflows should reference these standards to ensure consistent, high-quality interactions.** 
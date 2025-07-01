# 🗂️ Memory Commands Reference

**Status**: Authoritative & Up-to-date (auto-sourced from `ai-memory-aliases.sh` and `advanced-memory-aliases.sh`)

> Use this document as the single source of truth for all CLI commands that interact with the Memory-C* system. Other documentation SHOULD link here instead of duplicating command lists.

---

## 📥 Context Retrieval

| Command | Description |
|---------|-------------|
| `ai-get-context "query" [type]` | Retrieve rich AI context with confidence scoring |
| `ai-ctx-tech "query"` | Technical context (code, frameworks, debugging) |
| `ai-ctx-project "query"` | Project-specific context (features, milestones) |
| `ai-ctx-workflow "query"` | Workflow & process context |
| `ai-ctx-pref "query"` | User preference context |
| `ai-ctx "query"` | Quick generic context retrieval |
| `ai-context "query" [type]` | Legacy full-context retrieval |
| `ai-auto-search` | Automatic contextual memory search |
| `ai-search "query" [category]` | Manual memory search with advanced filters |
| `mem-search "query"` | Legacy basic search (deprecated) |

---

## 📝 Memory Storage

| Command | Description |
|---------|-------------|
| `ai-add-smart "text"` | Store insight with auto-categorisation |
| `ai-add "text" [CATEGORY]` | Add memory with explicit category |
| `ai-add-adv "text"` | Advanced add with full metadata |
| `mem-add "text"` | Legacy basic add (deprecated) |

> **Categories**: `TECHNICAL`, `PREFERENCE`, `PROJECT`, `WORKFLOW`, `LEARNING`, `SYSTEM`, `ERROR`, `INSIGHT`

---

## 📊 System Intelligence & Utilities

| Command | Description |
|---------|-------------|
| `ai-analytics` | Memory system analytics & statistics |
| `mem-analytics` | Legacy analytics (deprecated) |
| `mem-health` | Check Memory API health |
| `mem-ui` | Launch Memory UI dashboard (http://localhost:3010) |
| `ai-demo` | Run interactive demonstration of memory capabilities |

---

## 🛠️ Scripts & Setup

To load all commands in the current shell session:

```bash
source ai-memory-aliases.sh       # Core AI memory commands
source advanced-memory-aliases.sh # Enterprise-grade commands
```

To make the commands permanent add the two `source` lines to your `~/.bashrc` or shell RC file.

---

## 📝 Maintenance Notes

- **Canonical Location**: This file replaces any duplicated command listings in other documentation.
- **Updates**: Whenever aliases are added or changed, update this file **first** and link elsewhere.
- **Deprecation**: Legacy commands remain documented for backward compatibility but are not recommended for new workflows.
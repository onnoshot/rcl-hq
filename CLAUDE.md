# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Agent Workspace

A local-first, markdown-only multi-agent system. No code, no database — every agent is a folder of `.md` files. Claude Code is the runtime.

## Architecture

```
Human → Orchestrator → Agents → outputs/ & journal/
                                     ↕
                               journal/ (shared memory)
                                     ↕
                               knowledge/ (read-only reference)
```

**Key principle:** Agents never communicate directly. They coordinate through `journal/`. `knowledge/` is static — agents read it, never write to it. Only the human modifies `knowledge/`.

## System-Level Files

| File | Role |
|------|------|
| `AGENT_REGISTRY.md` | Master list of all agents — update when creating or retiring an agent |
| `CONVENTIONS.md` | Naming rules and structural requirements |
| `NEW_AGENT_BOOTSTRAP.md` | Step-by-step guide for creating a new agent |
| `AGENT_CREATION_CHECKLIST.md` | Verification checklist before activating an agent |
| `orchestrator/IDENTITY.md` | What the orchestrator does and does not do |

## Creating a New Agent

1. `cp -r agents/standard-agent agents/[your-agent-name]` (lowercase, hyphen-separated)
2. Fill in `AGENT.md`: mission (1 sentence), goals table with KPIs, non-goals
3. Create skills in `skills/` using `skills/_SKILL_TEMPLATE.md` — each skill must map to a goal
4. Fill in `HEARTBEAT.md`: schedule, cycle steps (read → assess → execute → log), weekly review
5. Fill in `RULES.md`: can/cannot lists, handoff rules
6. Register in `AGENT_REGISTRY.md`
7. Verify against `AGENT_CREATION_CHECKLIST.md`

## Agent Internal Structure

Every agent folder (`agents/[name]/`) contains:

| File/Folder | Purpose |
|-------------|---------|
| `AGENT.md` | Mission, Goals & KPIs, skills index, input/output contracts |
| `HEARTBEAT.md` | Cron schedule, cycle steps, weekly review, escalation rules |
| `MEMORY.md` | Agent-local learnings only — starts empty, earned from real data |
| `RULES.md` | Hard boundaries, handoff rules, shared knowledge read/write rules |
| `skills/` | One `.md` per skill (use `_SKILL_TEMPLATE.md`) |
| `data/imports/` | Human-provided data drops |
| `outputs/` | Agent-produced files (date-prefixed: `YYYY-MM-DD_agent-name_description.md`) |
| `scripts/` | Automation scripts — must be idempotent |

## Each Agent Cycle (Heartbeat)

```
1. READ CONTEXT   — journal/ (recent entries), knowledge/STRATEGY.md, own MEMORY.md
2. ASSESS STATE   — pipeline status, most valuable action, which skill to run
3. EXECUTE SKILL  — one skill per cycle unless there's a strong reason to combine
4. LOG            — write to journal/, update MEMORY.md, save output to outputs/
```

## Conventions

- Agent folder names: lowercase, hyphen-separated (`youtube`, `newsletter`, `customer-support`)
- Output files: `YYYY-MM-DD_agent-name_description.md`
- Journal entries: `YYYY-MM-DD_HHMM.md`
- Never overwrite an existing output file — always create a new dated one
- Scripts must be idempotent

## Hard Rules for All Agents

- Agents write to `journal/` and their own `outputs/` — never to `knowledge/`
- Agents do not modify other agents' files
- Nothing is published externally without human approval
- `MEMORY.md` starts empty — no pre-filled assumptions; patterns are earned from real data
- If a skill doesn't serve a goal in `AGENT.md`, delete it

## Reference Example

`examples/podcast-agent/` is a complete, working reference agent. Study it before creating a new one.

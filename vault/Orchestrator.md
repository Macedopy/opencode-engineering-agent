# Orchestrator

The **Orchestrator** is the default primary agent of this project. It receives
the user's request, decomposes it, and delegates to specialized subagents.

Workflow for a full feature request:

1. [[Researcher]] gathers context (codebase + vault)
2. [[Planner]] turns findings into actionable steps
3. [[Coder]] implements the plan
4. [[Reviewer]] verifies and corrects the output

The Orchestrator never edits files itself; it only delegates and consolidates.

#agent #architecture

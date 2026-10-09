# Multi-Agent Knowledge Base with OpenCode

A demo project that combines **custom OpenCode agents** with an **Obsidian
vault** used as a persistent knowledge base. A primary **Orchestrator**
delegates work to specialized subagents, and every agent can consult the vault
for domain context (contracts and business rules).

<!-- Paste your architecture diagram here -->

## Architecture

<img width="758" height="763" alt="OpenCode Custom agent drawio" src="https://github.com/user-attachments/assets/3170321d-a2b7-49d5-adf2-bd51c2ae0be4" />

| Agent | Mode | Can edit? | Responsibility |
| --- | --- | --- | --- |
| `orchestrator` | primary | no | Decomposes the request, delegates, consolidates |
| `researcher` | subagent | no | Gathers context from code + vault |
| `planner` | subagent | no | Turns findings into an ordered plan |
| `coder` | subagent | yes | Implements the plan |
| `reviewer` | subagent | no | Verifies against the plan and business rules |
| `vault-graph` | subagent | no | Answers structural questions about the vault |

## Repository layout

```text
.
├── .opencode/agents/        # custom agents (Markdown + YAML frontmatter)
│   ├── orchestrator.md
│   ├── researcher.md
│   ├── planner.md
│   ├── coder.md
│   ├── reviewer.md
│   └── vault-graph.md
├── vault/                   # Obsidian vault (Markdown notes)
│   ├── Orchestrator.md
│   ├── Researcher.md
│   ├── Planner.md
│   ├── Coder.md
│   ├── Reviewer.md
│   ├── Business Rules.md
│   ├── API Contract.md
│   ├── Wikilinks.md
│   ├── Graph View.md
│   └── graph.json           # generated index (nodes + edges)
├── build_graph.py           # extracts the vault graph from wikilinks
├── opencode.jsonc           # OpenCode project configuration
└── README.md
```

## Step-by-step: integrating a custom agent into OpenCode

### Step 1 — Create the agent file

Agents are Markdown files with YAML frontmatter. The filename becomes the
agent ID, and the document body becomes its system prompt.

```md title=".opencode/agents/vault-graph.md"
---
description: Analyzes the link graph of the knowledge base vault
mode: subagent
model: anthropic/claude-sonnet-4-5#high
color: "#38bdf8"
permissions:
  - action: read
    resource: "vault/**"
    effect: allow
  - action: edit
    resource: "*"
    effect: deny
  - action: subagent
    resource: "*"
    effect: deny
---

You are an expert at analyzing the Obsidian vault in `vault/`.
Answer using graph.json and the wikilinks between notes.
```

**Supported frontmatter fields**

| Field | Meaning |
| --- | --- |
| `description` | What the agent does. The orchestrator's model reads this to decide when to launch it |
| `mode` | `primary`, `subagent`, or `all` |
| `model` | `provider/model#variant`. Inherits the parent model when omitted |
| `permissions` | Ordered `{ action, resource, effect }` rules — last match wins |
| `steps` | Maximum number of model steps |
| `hidden` | Hides the agent from listings and the subagent catalog |
| `color` | Six-digit hex color for the UI |
| `disabled` | Removes a built-in or custom agent |

**Permission actions**: `read`, `glob`, `grep`, `edit`, `shell`, `webfetch`,
`websearch`, `skill`, `subagent`, and `*`. Effects are `allow`, `ask`, or
`deny`.

### Step 2 — Set the default agent

```jsonc title="opencode.jsonc"
{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "orchestrator"
}
```

### Step 3 — Control which subagents an agent may launch

Deny by default, then allow the workers explicitly:

```yaml
permissions:
  - action: subagent
    resource: "*"
    effect: deny
  - action: subagent
    resource: "researcher"
    effect: allow
  - action: subagent
    resource: "coder"
    effect: allow
```

### Step 4 — Give the agents access to the vault

Permission resources are matched against paths, so a relative pattern keeps
the repository portable:

```yaml
permissions:
  - action: read
    resource: "vault/**"
    effect: allow
```

### Step 5 — Generate the graph index from wikilinks

Obsidian stores notes as Markdown; the knowledge graph is implied by the
`[[wikilinks]]` between them. Extract it once and let the agents read a
machine-readable index:

```bash
py build_graph.py
```

Output:

```text
OK: 10 nodes, 22 edges -> vault/graph.json
```

### Step 6 — Open the vault in Obsidian (optional)

*Open folder as vault* → select `vault/`. Open the graph view to see the same
topology the agent sees.

### Step 7 — Run it

```bash
cd opencode-agent-demo
opencode
```

Then ask something like:

```text
Add a /health endpoint following our API contract
```

You should see the orchestrator delegate to `researcher`, then `planner`, then
`coder`, and finally `reviewer`.

## Design decisions worth explaining

- **Only the coder writes.** Every other agent denies `edit`, so the blast
  radius of a mistake is one agent.
- **No subagent can spawn another.** `subagent: deny` on every worker keeps the
  tree shallow and predictable.
- **The orchestrator delegates only.** It has read access for context, but
  editing is denied, so implementation always goes through a worker.
- **Descriptions matter.** The orchestrator picks subagents by reading their
  `description`, so they must state *when* to use each agent.
- **Centralized or distributed vault access.** Either let `researcher` gather
  everything and pass it along (cheaper), or let each agent query the vault
  directly (more faithful, more tokens). Both are configured here.

## Adding a vector store

The vault graph answers structural questions ("what is related to X?"). For
semantic search, connect an MCP server exposing a vector store
(pgvector, Qdrant, Chroma) and the agents gain a second retrieval path without
changing their prompts:

```bash
opencode mcp add <name> --url <mcp-endpoint>
```

## License

MIT

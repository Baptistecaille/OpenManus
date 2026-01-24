# OpenManus Architecture

This document provides a comprehensive overview of the OpenManus project structure, its components, and how they interact.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
  - [Agents](#agents)
  - [Tools](#tools)
  - [Flows](#flows)
  - [MCP (Model Context Protocol)](#mcp-model-context-protocol)
  - [Skills](#skills)
  - [Sandbox](#sandbox)
- [Data Flow](#data-flow)
- [Configuration](#configuration)
- [Entry Points](#entry-points)

---

## Overview

OpenManus is a modular AI agent framework built with the following design principles:

- **Extensibility**: Easy to add new agents, tools, and capabilities
- **Modularity**: Components are loosely coupled and can be swapped
- **Multi-LLM Support**: Works with OpenAI, Anthropic, Azure, Ollama, Bedrock, etc.
- **Safety**: Optional sandbox execution environment

```
┌─────────────────────────────────────────────────────────────────┐
│                        Entry Points                              │
│              main.py │ run_flow.py │ run_mcp.py                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Agents                                  │
│         Manus │ SWEAgent │ DataAnalysis │ MCPAgent              │
└─────────────────────────────────────────────────────────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│     Tools       │   │     Flows       │   │    Skills       │
│  PythonExecute  │   │  PlanningFlow   │   │  SkillManager   │
│  StrReplace     │   │  BaseFlow       │   │  SkillMatcher   │
│  WebSearch      │   │                 │   │                 │
│  Browser        │   │                 │   │                 │
└─────────────────┘   └─────────────────┘   └─────────────────┘
        │                                           │
        ▼                                           ▼
┌─────────────────┐                       ┌─────────────────┐
│    Sandbox      │                       │   MCP Servers   │
│  DockerSandbox  │                       │  External Tools │
└─────────────────┘                       └─────────────────┘
```

---

## Project Structure

```
OpenManus/
├── app/                          # Main application code
│   ├── agent/                    # Agent implementations
│   │   ├── base.py              # BaseAgent - abstract base class
│   │   ├── toolcall.py          # ToolCallAgent - base for tool-using agents
│   │   ├── manus.py             # Manus - main general-purpose agent
│   │   ├── swe.py               # SWEAgent - software engineering agent
│   │   ├── data_analysis.py     # DataAnalysis - data analysis agent
│   │   ├── mcp.py               # MCPAgent - MCP-enabled agent
│   │   └── react.py             # ReActAgent - ReAct paradigm agent
│   │
│   ├── tool/                     # Tool implementations
│   │   ├── base.py              # BaseTool - abstract base class
│   │   ├── tool_collection.py   # ToolCollection - manages multiple tools
│   │   ├── python_execute.py    # Execute Python code
│   │   ├── str_replace_editor.py# File editing tool
│   │   ├── bash.py              # Bash command execution
│   │   ├── webfetch.py          # Web fetching tool
│   │   ├── planning.py          # Planning/task management tool
│   │   ├── terminate.py         # Terminates agent execution
│   │   ├── mcp.py               # MCP client tools
│   │   ├── human_in_the_loop.py # Human interaction tool
│   │   ├── search/              # Search engines
│   │   │   ├── base.py          # BaseSearch
│   │   │   ├── google_search.py # Google search
│   │   │   ├── duckduckgo_search.py
│   │   │   └── baidu_search.py
│   │   ├── sandbox/             # Sandbox-specific tools
│   │   │   ├── sb_shell_tool.py # Sandboxed shell
│   │   │   ├── sb_files_tool.py # Sandboxed file operations
│   │   │   └── sb_browser_tool.py
│   │   └── chart_visualization/ # Data visualization tools
│   │       ├── data_visualization.py
│   │       ├── chart_prepare.py
│   │       └── python_execute.py
│   │
│   ├── flow/                     # Multi-agent orchestration
│   │   ├── base.py              # BaseFlow - abstract base class
│   │   ├── planning.py          # PlanningFlow - plan-based execution
│   │   └── flow_factory.py      # Flow creation factory
│   │
│   ├── prompt/                   # System prompts
│   │   ├── manus.py             # Manus agent prompts
│   │   ├── swe.py               # SWE agent prompts
│   │   ├── visualization.py     # Data visualization prompts
│   │   ├── planning.py          # Planning prompts
│   │   └── browser.py           # Browser interaction prompts
│   │
│   ├── sandbox/                  # Sandbox execution environment
│   │   ├── client.py            # Sandbox client interface
│   │   └── core/
│   │       ├── sandbox.py       # DockerSandbox implementation
│   │       ├── manager.py       # Sandbox manager
│   │       └── terminal.py      # Terminal emulation
│   │
│   ├── skills/                   # Skills system
│   │   ├── skill.py             # Skill data models
│   │   ├── skill_manager.py     # Discovers and loads skills
│   │   ├── skill_matcher.py     # LLM-based skill matching
│   │   ├── skill_parser.py      # YAML/Markdown parsing
│   │   └── hooks.py             # Skill lifecycle hooks
│   │
│   ├── mcp_server/               # MCP server implementation
│   │   └── server.py            # MCP server for OpenManus
│   │
│   ├── config.py                 # Configuration management
│   ├── llm.py                    # LLM client abstraction
│   ├── schema.py                 # Data schemas and types
│   ├── logger.py                 # Logging configuration
│   └── exceptions.py             # Custom exceptions
│
├── config/                       # Configuration files
│   ├── config.example.toml      # Example configuration
│   └── config.toml              # User configuration (gitignored)
│
├── skills/                       # User-defined skills
│   └── human-in-the-loop/       # Example skill
│       └── SKILL.md
│
├── mcp-servers/                  # External MCP servers
│   └── Office-Word-MCP-Server/  # Word document MCP server
│
├── main.py                       # Single agent entry point
├── run_flow.py                   # Multi-agent entry point
├── run_mcp.py                    # MCP-enabled entry point
└── requirements.txt              # Python dependencies
```

---

## Core Components

### Agents

Agents are the core execution units that process user requests and interact with tools.

#### Inheritance Hierarchy

```
BaseAgent (abstract)
    │
    └── ToolCallAgent
            │
            ├── Manus          # General-purpose agent
            ├── SWEAgent       # Software engineering agent
            ├── DataAnalysis   # Data analysis agent
            └── MCPAgent       # MCP-enabled agent
```

#### BaseAgent (`app/agent/base.py`)

The abstract base class providing:

| Feature | Description |
|---------|-------------|
| **State Management** | `IDLE`, `RUNNING`, `FINISHED`, `ERROR`, `SUSPENDED` |
| **Memory** | Stores conversation history |
| **Step Execution** | Main execution loop with `max_steps` limit |
| **Skills Integration** | Skill discovery, matching, and application |
| **Stuck Detection** | Detects and handles repeated responses |

```python
class BaseAgent(BaseModel, ABC):
    name: str
    description: Optional[str]
    system_prompt: Optional[str]
    llm: LLM
    memory: Memory
    state: AgentState
    max_steps: int = 10
    skill_manager: SkillManager
```

#### Manus (`app/agent/manus.py`)

The main general-purpose agent with MCP support:

```python
class Manus(ToolCallAgent):
    available_tools: ToolCollection = ToolCollection(
        PythonExecute(),
        StrReplaceEditor(),
        HumanInTheLoop(),
        Terminate(),
    )
    mcp_clients: MCPClients  # Connects to MCP servers
```

#### SWEAgent (`app/agent/swe.py`)

Specialized for software engineering tasks:

```python
class SWEAgent(ToolCallAgent):
    available_tools: ToolCollection = ToolCollection(
        Bash(),
        StrReplaceEditor(),
        Terminate()
    )
```

#### DataAnalysis (`app/agent/data_analysis.py`)

Focused on data analysis and visualization:

```python
class DataAnalysis(ToolCallAgent):
    available_tools: ToolCollection = ToolCollection(
        NormalPythonExecute(),
        VisualizationPrepare(),
        DataVisualization(),
        Terminate(),
    )
```

---

### Tools

Tools are callable capabilities that agents can use to interact with the environment.

#### BaseTool (`app/tool/base.py`)

```python
class BaseTool(ABC, BaseModel):
    name: str
    description: str
    parameters: Optional[dict]

    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""

    def to_param(self) -> Dict:
        """Convert to OpenAI function calling format."""
```

#### ToolResult

Standardized result object for all tool executions:

```python
class ToolResult(BaseModel):
    output: Any = None
    error: Optional[str] = None
    base64_image: Optional[str] = None
    system: Optional[str] = None
```

#### Available Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| `PythonExecute` | Execute Python code | Data processing, calculations |
| `StrReplaceEditor` | File editing with search/replace | Code modifications |
| `Bash` | Execute shell commands | System operations |
| `WebSearch` | Search the web | Information retrieval |
| `WebFetch` | Fetch web page content | Web scraping |
| `PlanningTool` | Create and manage task plans | Multi-step task planning |
| `Terminate` | End agent execution | Task completion |
| `HumanInTheLoop` | Request human input | Clarification, approval |
| `DataVisualization` | Create charts and graphs | Data visualization |

#### ToolCollection (`app/tool/tool_collection.py`)

Manages a collection of tools with lookup and iteration:

```python
class ToolCollection(BaseModel):
    tools: Tuple[BaseTool, ...]
    tool_map: Dict[str, BaseTool]

    def get_tool(self, name: str) -> Optional[BaseTool]
    def add_tools(self, *tools: BaseTool)
    def to_params(self) -> List[Dict]  # For LLM function calling
```

---

### Flows

Flows orchestrate multiple agents for complex tasks.

#### BaseFlow (`app/flow/base.py`)

```python
class BaseFlow(BaseModel, ABC):
    agents: Dict[str, BaseAgent]
    primary_agent_key: Optional[str]

    async def execute(self, input_text: str) -> str:
        """Execute the flow with given input."""
```

#### PlanningFlow (`app/flow/planning.py`)

Implements plan-based multi-agent execution:

```
┌──────────────────────────────────────────────────────────────┐
│                      PlanningFlow                             │
│                                                               │
│  1. Create Plan ──► 2. Get Current Step ──► 3. Select Agent  │
│         │                    │                     │          │
│         ▼                    ▼                     ▼          │
│  ┌─────────────┐     ┌─────────────┐      ┌─────────────┐   │
│  │ Planning    │     │ Step Status │      │  Execute    │   │
│  │ Tool        │     │ Tracker     │      │  Agent      │   │
│  └─────────────┘     └─────────────┘      └─────────────┘   │
│                                                   │          │
│                  4. Mark Complete ◄───────────────┘          │
│                           │                                   │
│                           ▼                                   │
│                  5. Next Step or Finalize                     │
└──────────────────────────────────────────────────────────────┘
```

**Step Statuses:**
- `NOT_STARTED` → `[ ]`
- `IN_PROGRESS` → `[→]`
- `COMPLETED` → `[✓]`
- `BLOCKED` → `[!]`

---

### MCP (Model Context Protocol)

MCP enables agents to connect to external tool servers.

#### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Manus Agent                           │
│                             │                                │
│                     ┌───────┴───────┐                       │
│                     │  MCPClients   │                       │
│                     └───────┬───────┘                       │
│               ┌─────────────┼─────────────┐                 │
│               ▼             ▼             ▼                 │
│        ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│        │ SSE      │  │ STDIO    │  │ STDIO    │            │
│        │ Server   │  │ Server 1 │  │ Server 2 │            │
│        └──────────┘  └──────────┘  └──────────┘            │
└─────────────────────────────────────────────────────────────┘
```

#### MCPClients (`app/tool/mcp.py`)

```python
class MCPClients(ToolCollection):
    sessions: Dict[str, ClientSession]

    async def connect_sse(self, server_url: str, server_id: str)
    async def connect_stdio(self, command: str, args: List[str], server_id: str)
    async def disconnect(self, server_id: str = "")
```

#### MCPClientTool

Proxy tool that calls remote MCP server methods:

```python
class MCPClientTool(BaseTool):
    session: Optional[ClientSession]
    server_id: str
    original_name: str

    async def execute(self, **kwargs) -> ToolResult:
        result = await self.session.call_tool(self.original_name, kwargs)
        return ToolResult(output=result)
```

#### Configuration

```toml
[mcp.servers.word]
type = "stdio"
command = "python"
args = ["-m", "word_document_server"]

[mcp.servers.browser]
type = "sse"
url = "http://localhost:8080/mcp"
```

---

### Skills

Skills are reusable instruction sets that can be dynamically applied to agents.

#### Skill Structure

```
skills/
└── my-skill/
    ├── SKILL.md           # Required: Instructions + YAML frontmatter
    ├── reference.md       # Optional: Reference documentation
    ├── examples/          # Optional: Example files
    └── scripts/           # Optional: Helper scripts
```

#### SKILL.md Format

```markdown
---
name: my-skill
description: What this skill does and when to use it
allowed_tools:
  - python_execute
  - str_replace_editor
model: gpt-4o  # Optional: specific model for this skill
hooks:
  on_start:
    - type: log
      message: "Skill activated"
---

# My Skill

Instructions for the agent when this skill is active...
```

#### Skill Components

| Component | Description |
|-----------|-------------|
| `Skill` | Data model containing metadata + content |
| `SkillMetadata` | Parsed YAML frontmatter |
| `SkillManager` | Discovers and loads skills from filesystem |
| `SkillMatcher` | LLM-based matching of requests to skills |
| `HookManager` | Manages skill lifecycle hooks |

#### Skill Matching Flow

```
User Request
     │
     ▼
┌─────────────────┐
│ SkillMatcher    │ ─── Uses LLM to find best skill
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SkillManager    │ ─── Loads skill from disk
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ BaseAgent       │ ─── Applies skill (modifies system prompt)
└─────────────────┘
```

---

### Sandbox

Secure containerized execution environment using Docker.

#### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     LocalSandboxClient                       │
│                            │                                 │
│                   ┌────────┴────────┐                       │
│                   │  DockerSandbox  │                       │
│                   └────────┬────────┘                       │
│                            │                                 │
│              ┌─────────────┼─────────────┐                  │
│              ▼             ▼             ▼                  │
│        ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│        │ Terminal │ │  Files   │ │  Network │              │
│        └──────────┘ └──────────┘ └──────────┘              │
└─────────────────────────────────────────────────────────────┘
```

#### SandboxSettings

```toml
[sandbox]
use_sandbox = true
image = "python:3.12-slim"
work_dir = "/workspace"
memory_limit = "1g"
cpu_limit = 2.0
timeout = 300
network_enabled = true
```

#### Sandbox Client Interface

```python
class BaseSandboxClient(ABC):
    async def create(self, config: SandboxSettings) -> None
    async def run_command(self, command: str, timeout: int) -> str
    async def copy_from(self, container_path: str, local_path: str)
    async def copy_to(self, local_path: str, container_path: str)
    async def read_file(self, path: str) -> str
    async def write_file(self, path: str, content: str)
    async def cleanup(self) -> None
```

---

## Data Flow

### Single Agent Execution (`main.py`)

```
User Input
     │
     ▼
┌─────────────────┐
│   Manus Agent   │
│                 │
│  1. Analyze     │ ─── Check if tools needed
│  2. Think       │ ─── LLM decides next action
│  3. Execute     │ ─── Run selected tool
│  4. Observe     │ ─── Process tool result
│  5. Repeat      │ ─── Until done or max_steps
│                 │
└────────┬────────┘
         │
         ▼
    Final Response
```

### Multi-Agent Flow (`run_flow.py`)

```
User Input
     │
     ▼
┌─────────────────┐
│  PlanningFlow   │
│                 │
│  1. Create Plan │ ─── LLM generates step-by-step plan
│                 │
│  2. For each step:
│     a. Select Agent (Manus / DataAnalysis / SWE)
│     b. Execute Step
│     c. Mark Complete
│                 │
│  3. Finalize    │ ─── Generate summary
│                 │
└────────┬────────┘
         │
         ▼
    Final Response
```

---

## Configuration

### Configuration File (`config/config.toml`)

```toml
# LLM Configuration
[llm]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."
max_tokens = 4096
temperature = 0.0

# Vision Model (optional)
[llm.vision]
model = "gpt-4o"
...

# Browser Settings
[browser]
headless = false

# Search Settings
[search]
engine = "Google"
fallback_engines = ["DuckDuckGo", "Bing"]

# Sandbox Settings
[sandbox]
use_sandbox = false
image = "python:3.12-slim"

# MCP Servers
[mcp.servers.word]
type = "stdio"
command = "python"
args = ["-m", "word_document_server"]

# Multi-Agent Flow
[runflow]
use_data_analysis_agent = true
```

---

## Entry Points

| Entry Point | Description | Usage |
|-------------|-------------|-------|
| `main.py` | Single Manus agent | `python main.py` |
| `run_flow.py` | Multi-agent with planning | `python run_flow.py` |
| `run_mcp.py` | MCP-enabled agent | `python run_mcp.py` |
| `app/server.py` | HTTP API server | `python -m app.server` |

---

## Extending OpenManus

### Adding a New Tool

1. Create a new file in `app/tool/`:

```python
from app.tool.base import BaseTool, ToolResult

class MyTool(BaseTool):
    name: str = "my_tool"
    description: str = "What my tool does"
    parameters: dict = {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "..."},
        },
        "required": ["param1"]
    }

    async def execute(self, param1: str, **kwargs) -> ToolResult:
        # Your logic here
        return ToolResult(output="result")
```

2. Add to an agent's `available_tools`:

```python
available_tools: ToolCollection = ToolCollection(
    MyTool(),
    ...
)
```

### Adding a New Agent

1. Create a new file in `app/agent/`:

```python
from app.agent.toolcall import ToolCallAgent

class MyAgent(ToolCallAgent):
    name: str = "my_agent"
    description: str = "What my agent does"
    system_prompt: str = "..."
    available_tools: ToolCollection = ToolCollection(...)
```

### Adding a New Skill

1. Create a directory in `skills/`:

```
skills/my-skill/
└── SKILL.md
```

2. Write the SKILL.md with YAML frontmatter:

```markdown
---
name: my-skill
description: When to use this skill
---

# Instructions

Your skill instructions here...
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

<p align="center">
  <img src="assets/logo.jpg" width="200"/>
</p>

<h1 align="center">OpenManus</h1>

<p align="center">
  <strong>An open-source framework for building general AI agents</strong>
</p>

<p align="center">
  English | <a href="README_zh.md">中文</a> | <a href="README_ko.md">한국어</a> | <a href="README_ja.md">日本語</a>
</p>

<p align="center">
  <a href="https://github.com/FoundationAgents/OpenManus/stargazers"><img src="https://img.shields.io/github/stars/FoundationAgents/OpenManus?style=social" alt="GitHub stars"></a>
  &ensp;
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  &ensp;
  <a href="https://discord.gg/DYn29wFk9z"><img src="https://dcbadge.vercel.app/api/server/DYn29wFk9z?style=flat" alt="Discord"></a>
  &ensp;
  <a href="https://huggingface.co/spaces/lyh-917/OpenManusDemo"><img src="https://img.shields.io/badge/Demo-Hugging%20Face-yellow" alt="Demo"></a>
  &ensp;
  <a href="https://doi.org/10.5281/zenodo.15186407"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.15186407.svg" alt="DOI"></a>
</p>

---

## Table of Contents

- [About](#about)
- [Key Features](#key-features)
- [Demo](#demo)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Advanced Usage](#advanced-usage)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Community](#community)
- [Sponsors](#sponsors)
- [Acknowledgements](#acknowledgements)
- [Citation](#citation)
- [License](#license)

---

## About

**OpenManus** is an open-source AI agent framework that enables you to build powerful autonomous agents capable of executing complex tasks. Unlike proprietary solutions that require invite codes, OpenManus empowers developers to create and deploy their own AI agents freely.

Built by the team behind [MetaGPT](https://github.com/geekan/MetaGPT), OpenManus was prototyped in just 3 hours and continues to evolve rapidly with community contributions.

> 🚀 **New!** Check out [OpenManus-RL](https://github.com/OpenManus/OpenManus-RL) — our sister project focused on reinforcement learning-based tuning methods (like GRPO) for LLM agents, developed in collaboration with UIUC researchers.

---

## Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-Agent Support** | Run single or multiple specialized agents collaboratively |
| 🌐 **Browser Automation** | Web browsing, scraping, and interaction via Playwright |
| 🔧 **Extensible Tools** | File operations, Python execution, web search, and more |
| 📊 **Data Analysis** | Built-in data analysis and visualization capabilities |
| 🔌 **MCP Integration** | Model Context Protocol support for enhanced tool usage |
| 🏖️ **Sandbox Mode** | Secure containerized execution environment |
| 🎯 **Multi-LLM Support** | OpenAI, Anthropic, Azure, Ollama, AWS Bedrock, and more |

---

## Demo

<p align="center">
  <a href="https://huggingface.co/spaces/lyh-917/OpenManusDemo">
    <img src="https://img.shields.io/badge/Try%20Live%20Demo-Hugging%20Face-yellow?style=for-the-badge" alt="Try Demo">
  </a>
</p>

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.12+ |
| Git | Latest |
| API Key | OpenAI, Anthropic, or compatible provider |

---

## Installation

Choose one of the two installation methods below:

### Method 1: Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone the repository
git clone https://github.com/FoundationAgents/OpenManus.git
cd OpenManus

# 3. Create and activate virtual environment
uv venv --python 3.12
source .venv/bin/activate  # Unix/macOS
# .venv\Scripts\activate   # Windows

# 4. Install dependencies
uv pip install -r requirements.txt
```

### Method 2: Using conda

```bash
# 1. Create conda environment
conda create -n open_manus python=3.12
conda activate open_manus

# 2. Clone the repository
git clone https://github.com/FoundationAgents/OpenManus.git
cd OpenManus

# 3. Install dependencies
pip install -r requirements.txt
```

### Optional: Browser Automation

If you plan to use browser automation features:

```bash
playwright install
```

---

## Configuration

### 1. Create Configuration File

```bash
cp config/config.example.toml config/config.toml
```

### 2. Configure Your LLM Provider

Edit `config/config.toml` with your preferred provider:

<details>
<summary><b>OpenAI</b></summary>

```toml
[llm]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."
max_tokens = 4096
temperature = 0.0
```
</details>

<details>
<summary><b>Anthropic Claude</b></summary>

```toml
[llm]
model = "claude-3-7-sonnet-20250219"
base_url = "https://api.anthropic.com/v1/"
api_key = "sk-ant-..."
max_tokens = 8192
temperature = 0.0
```
</details>

<details>
<summary><b>Azure OpenAI</b></summary>

```toml
[llm]
api_type = "azure"
model = "gpt-4o-mini"
base_url = "https://YOUR_ENDPOINT.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT"
api_key = "your-azure-api-key"
max_tokens = 8096
temperature = 0.0
api_version = "2024-08-01-preview"
```
</details>

<details>
<summary><b>Ollama (Local)</b></summary>

```toml
[llm]
api_type = "ollama"
model = "llama3.2"
base_url = "http://localhost:11434/v1"
api_key = "ollama"
max_tokens = 4096
temperature = 0.0
```
</details>

<details>
<summary><b>AWS Bedrock</b></summary>

```toml
[llm]
api_type = "aws"
model = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
base_url = "bedrock-runtime.us-west-2.amazonaws.com"
api_key = "placeholder"
max_tokens = 8192
temperature = 1.0
```
</details>

### 3. Optional: Vision Model

```toml
[llm.vision]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."
max_tokens = 4096
temperature = 0.0
```

### 4. Optional: Browser Settings

```toml
[browser]
headless = false  # Set to true to hide browser window
# chrome_instance_path = "/path/to/chrome"  # Use existing Chrome
```

---

## Quick Start

### Basic Usage

```bash
python main.py
```

Then enter your prompt in the terminal:

```
Enter your prompt: Search for the latest AI news and summarize the top 3 articles
```

### Example Prompts

| Task | Prompt |
|------|--------|
| **Web Research** | "Find and compare the pricing of the top 3 cloud providers" |
| **Code Generation** | "Create a Python script that scrapes weather data" |
| **Data Analysis** | "Analyze this CSV file and create visualizations" |
| **Automation** | "Log into my dashboard and export the monthly report" |

---

## Advanced Usage

### MCP Tool Version

For enhanced tool capabilities via Model Context Protocol:

```bash
python run_mcp.py
```

### Multi-Agent Flow

For complex tasks requiring multiple specialized agents:

```bash
python run_flow.py
```

### Data Analysis Agent

Enable the data analysis agent in `config/config.toml`:

```toml
[runflow]
use_data_analysis_agent = true
```

> 📖 See [Data Analysis Setup Guide](app/tool/chart_visualization/README.md#Installation) for additional dependencies.

### Sandbox Mode

Run agents in a secure containerized environment:

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

---

## Architecture

```
OpenManus/
├── app/
│   ├── agent/          # Agent implementations (Manus, SWE, Data Analysis)
│   ├── flow/           # Multi-agent orchestration
│   ├── prompt/         # System prompts
│   ├── tool/           # Tool implementations
│   │   ├── search/     # Search engines (Google, Bing, DuckDuckGo)
│   │   ├── sandbox/    # Sandboxed execution tools
│   │   └── chart_visualization/  # Data visualization
│   ├── sandbox/        # Container sandbox management
│   └── mcp_server/     # MCP server implementation
├── config/             # Configuration files
├── main.py             # Single agent entry point
├── run_flow.py         # Multi-agent entry point
└── run_mcp.py          # MCP-enabled entry point
```

---

## Troubleshooting

<details>
<summary><b>API Key errors</b></summary>

Ensure your API key is correctly set in `config/config.toml` and matches your provider's format:
- OpenAI: `sk-...`
- Anthropic: `sk-ant-...`
</details>

<details>
<summary><b>Browser automation not working</b></summary>

```bash
# Reinstall Playwright browsers
playwright install --force

# For headed mode issues, try:
playwright install chromium
```
</details>

<details>
<summary><b>Import errors</b></summary>

```bash
# Ensure you're in the virtual environment
source .venv/bin/activate

# Reinstall dependencies
uv pip install -r requirements.txt --force-reinstall
```
</details>

<details>
<summary><b>Rate limiting</b></summary>

Configure search fallback in `config/config.toml`:

```toml
[search]
engine = "Google"
fallback_engines = ["DuckDuckGo", "Bing"]
retry_delay = 60
max_retries = 3
```
</details>

---

## Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run pre-commit checks: `pre-commit run --all-files`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

📧 Questions? Contact [@mannaandpoem](https://github.com/mannaandpoem) at mannaandpoem@gmail.com

---

## Community

<div align="center">

[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/DYn29wFk9z)

</div>

Join our Feishu networking group to share experiences with other developers:

<div align="center">
  <img src="assets/community_group.jpg" alt="OpenManus Community" width="300" />
</div>

---

## Sponsors

<a href="https://ppinfra.com/user/register?invited_by=OCPKCN&utm_source=github_openmanus&utm_medium=github_readme&utm_campaign=link">
  <img src="https://img.shields.io/badge/PPIO-Computing%20Sponsor-blue?style=for-the-badge" alt="PPIO">
</a>

> **PPIO** — The most affordable and easily-integrated MaaS and GPU cloud solution.

---

## Acknowledgements

OpenManus builds upon the work of many excellent open-source projects:

**Core Dependencies:**
- [anthropic-computer-use](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo)
- [browser-use](https://github.com/browser-use/browser-use)
- [crawl4ai](https://github.com/unclecode/crawl4ai)

**Inspiration & Related Projects:**
- [MetaGPT](https://github.com/geekan/MetaGPT)
- [OpenHands](https://github.com/All-Hands-AI/OpenHands)
- [SWE-agent](https://github.com/SWE-agent/SWE-agent)
- [AAAJ](https://github.com/metauto-ai/agent-as-a-judge)

Special thanks to **stepfun (阶跃星辰)** for supporting our Hugging Face demo space.

---

## Citation

If you use OpenManus in your research, please cite:

```bibtex
@misc{openmanus2025,
  author = {Xinbin Liang and Jinyu Xiang and Zhaoyang Yu and Jiayi Zhang and Sirui Hong and Sheng Fan and Xiao Tang and Bang Liu and Yuyu Luo and Chenglin Wu},
  title = {OpenManus: An open-source framework for building general AI agents},
  year = {2025},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.15186407},
  url = {https://doi.org/10.5281/zenodo.15186407},
}
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <b>Built with ❤️ by the MetaGPT community</b>
</p>

<p align="center">
  <a href="#openmanus">Back to top ↑</a>
</p>

[![Star History Chart](https://api.star-history.com/svg?repos=FoundationAgents/OpenManus&type=Date)](https://star-history.com/#FoundationAgents/OpenManus&Date)

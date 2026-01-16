# OpenManus with Frontend & Skills System

This is the enhanced OpenManus project with:
- **Frontend Web Interface**: FastAPI-based web UI
- **Skills System**: Anthropic-style Agent Skills

## What's New

### 1. Frontend Web Interface

A complete web interface for interacting with OpenManus:

- Real-time task progress via SSE (Server-Sent Events)
- Multi-language support (EN, ZH, JA, KO, DE)
- LLM configuration management
- Task history and management
- Clean, responsive design

**Quick Start:**
```bash
# Start the frontend server
./run_frontend.sh

# Or directly
python frontend_app.py
```

Visit: http://0.0.0.0:8000

**Documentation:** See [docs/FRONTEND.md](docs/FRONTEND.md)

### 2. Skills System

Implement Agent Skills similar to Anthropic's Claude Code:

- **LLM-based Matching**: Automatically matches user requests to relevant skills
- **Progressive Disclosure**: Loads supporting files only when needed
- **Tool Restrictions**: Skills can specify allowed tools
- **Hooks System**: PreToolUse, PostToolUse, Stop event handlers
- **Multi-Agent Support**: Works with all BaseAgent subclasses

**Example Skills:**
- `skills/examples/code-review/` - Reviews code for quality and best practices
- `skills/examples/commit-message/` - Generates conventional commit messages
- `skills/examples/security-check/` - Security vulnerability scanning

**Quick Start:**
```python
from app.agent.manus import Manus

# Agent with skills automatically discovered
agent = await Manus.create()

# Skills are matched and applied automatically
await agent.run("Review my code")
```

**Documentation:** See [docs/SKILLS_GUIDE.md](docs/SKILLS_GUIDE.md)

## Project Structure

```
OpenManus/
├── app/
│   ├── agent/              # Agent implementations
│   │   ├── base.py       # With skill system integration
│   │   ├── toolcall.py   # With hooks support
│   │   └── manus.py      # Main agent
│   ├── skills/             # Skills system
│   │   ├── skill.py
│   │   ├── skill_parser.py
│   │   ├── skill_manager.py
│   │   ├── skill_matcher.py
│   │   ├── hooks.py
│   │   └── utils.py
│   └── ...               # Other modules
├── skills/                  # User skills directory
│   ├── examples/            # Example skills
│   └── README.md
├── static/                 # Frontend assets
│   ├── style.css
│   ├── main.js
│   └── i18n.js
├── templates/               # Frontend templates
│   └── index.html
├── frontend_app.py         # FastAPI web server
├── run_frontend.sh         # Frontend startup script
├── main.py                 # CLI interface (original)
├── config/                 # Configuration
└── docs/                   # Documentation
    ├── FRONTEND.md
    └── SKILLS_GUIDE.md
```

## Installation

### 1. Standard Installation

```bash
# Clone repository
git clone https://github.com/FoundationAgents/OpenManus.git
cd OpenManus

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Create config file
cp config/config.example.toml config/config.toml

# Edit with your API keys
nano config/config.toml
```

## Usage

### Using the Frontend (Recommended)

1. Start the frontend server:
   ```bash
   ./run_frontend.sh
   ```

2. Open browser to: http://0.0.0.0.0:8000

3. Configure LLM settings via the web interface

4. Create tasks and watch real-time progress

### Using the CLI

```bash
# Standard usage
python main.py

# With specific prompt
python main.py --prompt "Your task here"
```

### Creating Custom Skills

1. Create a skill directory:
   ```bash
   mkdir -p skills/my-skill
   ```

2. Add SKILL.md:
   ```markdown
   ---
   name: my-skill
   description: What this skill does
   ---

   # Instructions...
   ```

3. The skill is automatically discovered and matched!

## Testing

### Test Skills System

```bash
# Run standalone tests
python test_skills_standalone.py

# Or full tests
pytest tests/test_skills.py -v
```

### Test Frontend

```bash
# Start frontend
./run_frontend.sh
```

## Key Features

### Skills System Features

✓ **Automatic Discovery**: Skills loaded from `skills/` directory
✓ **LLM-based Matching**: Intelligent matching using language model
✓ **Tool Restrictions**: Skills can limit available tools
✓ **Hooks**: Event-driven actions (PreToolUse, PostToolUse, Stop)
✓ **Progressive Disclosure**: Supporting files loaded on-demand
✓ **Multi-Agent Support**: Works with all BaseAgent subclasses

### Frontend Features

✓ **Real-time Updates**: SSE streaming for live progress
✓ **Multi-language**: EN, ZH, JA, KO, DE support
✓ **Task Management**: Create, track, and manage tasks
✓ **Configuration UI**: Web-based LLM and server config
✓ **Task History**: View past tasks and results
✓ **Responsive Design**: Clean, modern interface

## Documentation

- [Frontend Guide](docs/FRONTEND.md) - Complete frontend documentation
- [Skills Guide](docs/SKILLS_GUIDE.md) - Skills system guide
- [Skills README](skills/README.md) - Skills directory documentation
- [Example Skills](skills/examples/) - Working skill examples

## Development

### Adding New Skills

1. Create skill in `skills/your-skill/SKILL.md`
2. Follow the [Skills Guide](docs/SKILLS_GUIDE.md)
3. Test with `test_skills_standalone.py`

### Extending Frontend

1. Add routes in `frontend_app.py`
2. Update templates in `templates/`
3. Add styles in `static/style.css`
4. Update i18n in `static/i18n.js`

## Troubleshooting

### Skills Not Loading

1. Ensure `skills/` directory exists
2. Check SKILL.md format (YAML frontmatter required)
3. Verify YAML syntax is correct
4. Check logs for parsing errors

### Frontend Not Starting

1. Check port 8000 is not in use
2. Verify dependencies installed: `pip list | grep -E "fastapi|uvicorn|jinja2"`
3. Check browser console for errors

### Configuration Issues

1. Ensure `config/config.toml` exists
2. Verify API key is valid
3. Check model name matches your API provider

## Contributing

Contributions welcome! Areas to contribute:

- New skills for common workflows
- Frontend UI improvements
- Additional language translations
- Bug fixes and performance improvements

## License

MIT License - See [LICENSE](LICENSE)

---

**Note**: This version integrates the frontend from the `front-end` branch and implements a complete skills system based on Anthropic's Agent Skills architecture.

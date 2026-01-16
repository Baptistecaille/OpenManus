# OpenManus Frontend

This is the FastAPI web interface for OpenManus.

## Features

- **Web Interface**: Clean, responsive UI for interacting with OpenManus
- **Real-time Updates**: SSE (Server-Sent Events) for live task progress
- **Task Management**: Create and track multiple tasks
- **Multi-language Support**: English, Chinese (中文), Japanese (日本語), Korean (한국어), German (Deutsch)
- **Configuration Management**: Configure LLM and server settings from the web interface
- **Task History**: View and manage past tasks

## Quick Start

### 1. Start the Frontend Server

```bash
# Using the run script (recommended)
./run_frontend.sh

# Or directly
python frontend_app.py
```

The frontend will be available at: `http://0.0.0.0:8000`

### 2. Configure LLM Settings

Before creating tasks, ensure your LLM configuration is set up:

1. Click the "Configuration" button in the top right
2. Fill in the LLM configuration (API key, model, base URL)
3. Configure server settings if needed
4. Click "Save Configuration"

The configuration will be saved to `config/config.toml`.

### 3. Create a Task

1. Enter your task prompt in the input field
2. Click "Create Task" or press Enter
3. The agent will start processing your request
4. Watch the real-time progress in the main panel

### 4. View Task History

Previous tasks are displayed in the left sidebar for easy reference.

## Architecture

```
frontend_app.py          # FastAPI web server
├── Routes
│   ├── /                  # Web interface
│   ├── /tasks              # Task management
│   ├── /tasks/{id}/events # SSE events stream
│   ├── /config/status     # Config status check
│   └── /config/save        # Save configuration
├── TaskManager        # In-memory task and queue management
└── Integration
    └── Manus Agent    # Backend agent execution
```

## Configuration

### LLM Configuration

The frontend reads LLM configuration from `config/config.toml`:

```toml
[llm]
[llm.default]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."
max_tokens = 4096
temperature = 0.0
```

### Server Configuration

```toml
[server]
host = "0.0.0.0"
port = 8000
```

If no server configuration is present, defaults to `0.0.0.0:8000`.

## API Endpoints

### GET /
Returns the web interface HTML page.

### POST /tasks
Create a new task.

**Request:**
```json
{
  "prompt": "Your task prompt here"
}
```

**Response:**
```json
{
  "task_id": "uuid-here"
}
```

### GET /tasks
List all tasks.

**Response:**
```json
[
  {
    "id": "uuid",
    "prompt": "Task description",
    "created_at": "2025-01-16T12:00:00",
    "status": "completed",
    "steps": [...]
  }
]
```

### GET /tasks/{task_id}
Get details of a specific task.

### GET /tasks/{task_id}/events
SSE (Server-Sent Events) stream for real-time task updates.

**Events:**
- `status`: Task status update with steps
- `think`: Agent thinking
- `tool`: Tool execution
- `act`: Agent action
- `run`: Execution step result
- `complete`: Task completed
- `error`: Task failed

### GET /config/status
Check if configuration file exists and return current config.

**Response:**
```json
{
  "status": "exists|missing|error",
  "config": { ... }
}
```

### POST /config/save
Save LLM and server configuration.

**Request:**
```json
{
  "llm": {
    "model": "gpt-4o",
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-...",
    "max_tokens": 4096,
    "temperature": 0.0
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  }
}
```

## Event Types

The frontend uses SSE to stream events to the client:

### Status Events

```javascript
{
  "type": "status",
  "status": "running|completed|failed",
  "steps": [...]
}
```

### Step Events

```javascript
{
  "type": "think|tool|act|run|error",
  "step": number,
  "result": "content",
  "data": { ... }
}
```

### Completion Events

```javascript
{
  "type": "complete",
  "data": { ... }
}
```

## Development

### Adding New Features

1. Add routes in `frontend_app.py`
2. Update templates in `templates/`
3. Add styles in `static/style.css`
4. Update i18n in `static/i18n.js`

### Testing

```bash
# Run tests
pytest tests/test_frontend.py -v
```

### File Structure

```
frontend_app.py              # Main FastAPI application
templates/
├── index.html            # Main web interface
static/
├── style.css              # Styles
├── main.js               # Frontend JavaScript
└── i18n.js              # Internationalization
```

## Integration with Backend

The frontend integrates with the OpenManus agent system through:

1. **Manus Agent**: Uses `app.agent.manus.Manus` for task execution
2. **Logger Integration**: Custom log handler to capture agent events
3. **Config Sharing**: Uses `app.config` for LLM settings

## Troubleshooting

### Port Already in Use

If you get "Address already in use":

```bash
# Change the port in config.toml
[server]
port = 8001

# Or run with custom port
uvicorn frontend_app:app --port 8001
```

### Config File Not Found

If the frontend can't read the config:

1. Ensure `config/config.toml` exists
2. Copy from example: `cp config/config.example.toml config/config.toml`
3. Fill in your API key

### CORS Issues

If you get CORS errors when accessing the API:

1. Check the CORS middleware configuration in `frontend_app.py`
2. Ensure allowed origins include your frontend URL
3. Verify your proxy settings

## License

This frontend is part of OpenManus and follows the same MIT license.

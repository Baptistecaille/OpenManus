from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import uuid
from typing import Dict, Optional, Any
from app.agent.manus import Manus
from app.tool.mcp import MCPClients
from app.config import config
from app.logger import logger
from contextlib import asynccontextmanager
from app.exceptions import AgentSuspend

# Global shared MCP clients
shared_mcp_clients = MCPClients()

# Global session storage: session_id -> Agent instance
# Note: In production this should be a proper cache (Redis) or limited size dict
sessions: Dict[str, Manus] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MCP servers once
    logger.info("Initializing shared MCP clients...")
    try:
        for server_id, server_config in config.mcp_config.servers.items():
            if server_config.type == "sse" and server_config.url:
                await shared_mcp_clients.connect_sse(server_config.url, server_id)
            elif server_config.type == "stdio" and server_config.command:
                await shared_mcp_clients.connect_stdio(
                    server_config.command,
                    server_config.args,
                    server_id
                )
        logger.info("Shared MCP clients initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize MCP clients: {e}")
    
    yield
    
    # Shutdown: Disconnect
    logger.info("Disconnecting shared MCP clients...")
    await shared_mcp_clients.disconnect()
    
    # Cleanup sessions
    for session_id, agent in sessions.items():
        if hasattr(agent, "cleanup"):
            await agent.cleanup()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    status: str = "completed" # completed, suspended, error
    session_id: Optional[str] = None
    question: Optional[str] = None # If suspended

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    logger.info(f"Processing request for session {session_id}")

    agent = None
    
    try:
        # Retrieve or create agent
        if session_id in sessions:
            logger.info(f"Resuming existing session {session_id}")
            agent = sessions[session_id]
            
            # If agent was suspended, we treat the prompt as the ANSWER to the question
            if request.prompt:
                # We need to manually inject the answer into the tool execution
                # The agent logic needs to support "resuming" a tool call
                if hasattr(agent, "_suspended_tool_call") and agent._suspended_tool_call:
                    logger.info(f"Resuming suspended tool with input: {request.prompt}")
                    agent._resume_suspended_tool(request.prompt)
                    # Result will be processed in the run loop below
        else:
            logger.info(f"Creating new session {session_id}")
            if not request.prompt.strip():
                raise HTTPException(status_code=400, detail="Prompt cannot be empty for new session")
            
            # Create new agent with shared MCP clients
            agent = await Manus.create(mcp_clients=shared_mcp_clients)
            sessions[session_id] = agent

        # Run the agent (or continue running)
        # If it was suspended, state was set to IDLE by _resume_suspended_tool, so run() works.
        # If new, state is IDLE, so run() works.
        # We pass request.prompt ONLY if it's a NEW request. 
        # If resuming, prompt is tool output, already handled above.
        run_input = request.prompt if session_id not in sessions else None # Logic slightly flawed
        
        # Correction:
        # New Session: run(prompt)
        # Existing Session (Resume): _resume_suspended_tool(prompt) -> run(None)
        
        input_prompt = request.prompt if request.session_id is None else None
        
        result = await agent.run(input_prompt)
        
        return ChatResponse(
            response=result,
            status="completed",
            session_id=session_id
        )

    except AgentSuspend as e:
        logger.info(f"Session {session_id} suspended: {e.question}")
        return ChatResponse(
            response=e.question, # Show question as response text
            status="suspended",
            session_id=session_id,
            question=e.question
        )
        
    except Exception as e:
        logger.error(f"Error during chat processing: {e}")
        # Clean up failed session? Maybe keep for debugging or retry?
        # For now, keep it simple
        return ChatResponse(
            response=f"Error: {str(e)}",
            status="error",
            session_id=session_id
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)

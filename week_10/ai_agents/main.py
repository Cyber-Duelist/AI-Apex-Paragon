from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import json
import os
import shutil
from first_agent import stream_agent

app = FastAPI(title="AI Agent Visualizer")

# Ensure directories exist
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
for d in [STATIC_DIR, UPLOAD_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class AgentRequest(BaseModel):
    messages: list

class ExecuteToolRequest(BaseModel):
    tool_name: str
    args: dict

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

@app.post("/api/execute_tool")
async def api_execute_tool(req: ExecuteToolRequest):
    from first_agent import execute_tool_manually
    result = execute_tool_manually(req.tool_name, req.args)
    return {"result": result}

@app.post("/api/stream_agent")
async def api_stream_agent(req: AgentRequest):
    def event_stream():
        # Iterate over the agent's yields and format them as Server-Sent Events (SSE)
        for event in stream_agent(req.messages):
            # Send the JSON payload prefixed with 'data: ' and followed by double newline
            # Use a custom JSON encoder to handle Pydantic objects from Groq API
            yield f"data: {json.dumps(event, default=lambda o: o.model_dump() if hasattr(o, 'model_dump') else str(o))}\n\n"
            
    return StreamingResponse(event_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

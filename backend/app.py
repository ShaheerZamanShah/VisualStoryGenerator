from __future__ import annotations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from backend.routes import assets, edit, pipeline
from backend.services.pipeline_service import PipelineService
from backend.websocket.manager import ConnectionManager
from shared.utils import get_settings

settings = get_settings()
app = FastAPI(title="AI Powered Animated Video Generation System")


class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        return response


app.add_middleware(CSPMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_origin,
        "http://localhost",
        "http://localhost:80",
        "http://localhost:8080",
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ws_manager = ConnectionManager()
pipeline_service = PipelineService(ws_manager)
app.include_router(pipeline.get_router(pipeline_service))
app.include_router(assets.router)
app.include_router(edit.get_router(ws_manager))


@app.websocket("/ws/progress/{job_id}")
async def progress_socket(websocket: WebSocket, job_id: str):
    await ws_manager.connect(job_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(job_id, websocket)


@app.get("/health")
async def health():
    return {"ok": True}

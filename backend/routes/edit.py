from __future__ import annotations

import asyncio
import threading
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, HTTPException

from agents.edit_agent.agent import EditAgent, EditAgentState
from agents.orchestrator.workflow import PipelineWorkflow
from backend.websocket.manager import ConnectionManager
from shared.schemas import EditRequest
from shared.utils import read_json
from state_manager.state_manager import StateManager

router = APIRouter(prefix="/api/edit", tags=["edit"])

# Lazy-initialised: created on first request so GROQ_API_KEY is loaded by then
_agent: EditAgent | None = None

# Per-job undo state stores — keyed by job_id
_job_states: Dict[str, EditAgentState] = {}
_state_manager = StateManager()

# WebSocket manager will be injected by app via `get_router`
_ws_manager: ConnectionManager | None = None


def _get_agent() -> EditAgent:
    global _agent
    if _agent is None:
        _agent = EditAgent()
    return _agent


def _get_state(job_id: str) -> EditAgentState:
    if job_id not in _job_states:
        _job_states[job_id] = EditAgentState({"job_id": job_id}, job_id=job_id)
    return _job_states[job_id]


def get_router(ws_manager: ConnectionManager) -> APIRouter:
    """Return the edit router and register the ConnectionManager for broadcasts."""
    global _ws_manager
    _ws_manager = ws_manager
    return router


@router.post("/{job_id}")
async def apply_edit(job_id: str, req: EditRequest):
    try:
        agent = _get_agent()
        state = _get_state(job_id)
        result = agent.handle(req.query, state)

        if getattr(result, "rerender_required", False):
            loop = asyncio.get_event_loop()

            def _rerender_thread():
                success = True
                try:
                    def _progress_cb(phase: str, status: str, percent: int, meta: Dict):
                        payload = {"phase": phase, "status": status, "percent": percent, "meta": meta}
                        if _ws_manager and loop:
                            asyncio.run_coroutine_threadsafe(_ws_manager.broadcast(job_id, payload), loop)

                    workflow = PipelineWorkflow(progress_cb=_progress_cb)
                    orig_story_path = f"data/outputs/{job_id}/story_spec.json"
                    timing_manifest_path = f"data/outputs/{job_id}/audio/timing_manifest.json"
                    master_audio_path = f"data/outputs/{job_id}/audio/master_dialogue.wav"

                    try:
                        story = read_json(orig_story_path)
                        job_state_path = Path(f"data/outputs/{job_id}/job_state.json")
                        job_state = read_json(job_state_path) if job_state_path.exists() else {}
                        original_prompt = job_state.get("user_prompt", "")
                        last_edit = state.state.get("last_edit", {})

                        revised = workflow.story_agent.revise(
                            job_id=job_id,
                            original_prompt=original_prompt,
                            current_story=story,
                            edit_request=req.query,
                            intent=last_edit.get("intent", "unknown"),
                            params=last_edit.get("params", {}),
                        )
                        story_spec_path = revised["story_spec_path"]
                    except Exception:
                        story_spec_path = orig_story_path

                    if _ws_manager and loop:
                        asyncio.run_coroutine_threadsafe(
                            _ws_manager.broadcast(
                                job_id,
                                {"phase": "edit", "status": "running", "percent": 75, "meta": {"msg": "Applying edit"}},
                            ),
                            loop,
                        )

                    workflow.run_audio(job_id, story_spec_path)
                    workflow.run_video(job_id, story_spec_path, timing_manifest_path, master_audio_path)

                except Exception as e:
                    success = False
                    if _ws_manager and loop:
                        asyncio.run_coroutine_threadsafe(
                            _ws_manager.broadcast(job_id, {"phase": "error", "status": "failed", "percent": 100, "meta": {"error": str(e)}}),
                            loop,
                        )
                finally:
                    if success and _ws_manager and loop:
                        asyncio.run_coroutine_threadsafe(
                            _ws_manager.broadcast(
                                job_id,
                                {"phase": "done", "status": "completed", "percent": 100, "meta": {"final_video_path": f"data/outputs/{job_id}/video/final_output.mp4"}},
                            ),
                            loop,
                        )

            thread = threading.Thread(target=_rerender_thread, daemon=True)
            thread.start()
        else:
            try:
                if _ws_manager:
                    payload = {
                        "phase": "done",
                        "status": "completed",
                        "percent": 100,
                        "meta": {"final_video_path": f"data/outputs/{job_id}/video/final_output.mp4"},
                    }
                    await _ws_manager.broadcast(job_id, payload)
            except Exception:
                pass

        return result.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{job_id}/undo")
async def undo_edit(job_id: str):
    try:
        agent = _get_agent()
        state = _get_state(job_id)
        result = agent.handle("undo", state)
        # Notify frontend that outputs were restored and it should reload the video
        try:
            if _ws_manager:
                payload = {
                    "phase": "done",
                    "status": "completed",
                    "percent": 100,
                    "meta": {"final_video_path": f"data/outputs/{job_id}/video/final_output.mp4"},
                }
                await _ws_manager.broadcast(job_id, payload)
        except Exception:
            pass
        return result.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{job_id}/history")
async def get_history(job_id: str):
    try:
        return {"job_id": job_id, "versions": _state_manager.list_versions(job_id)}
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))


from __future__ import annotations

from pathlib import Path

from state_manager.state_manager import StateManager
from state_manager.storage import Storage
from shared.utils import read_json


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_snapshot_stores_state_and_assets(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    sm = StateManager()
    sm.storage = Storage(root="state_versions")

    job_id = "job_a"
    outputs = Path("data/outputs") / job_id
    _write(outputs / "job_state.json", '{"status": "running"}')
    _write(outputs / "video" / "final_output.mp4", "fake-v1")

    v1 = sm.snapshot(job_id, {"step": 1}, note="first")
    assert v1 == 1

    versions = sm.list_versions(job_id)
    assert len(versions) == 1
    assert Path(versions[0]["state_path"]).exists()
    assert Path(versions[0]["assets_path"]).exists()


def test_undo_restores_previous_assets_and_state(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    sm = StateManager()
    sm.storage = Storage(root="state_versions")

    job_id = "job_b"
    outputs = Path("data/outputs") / job_id

    _write(outputs / "job_state.json", '{"status": "running", "version": 1}')
    _write(outputs / "video" / "final_output.mp4", "fake-v1")
    sm.snapshot(job_id, {"step": 1}, note="v1")

    _write(outputs / "job_state.json", '{"status": "running", "version": 2}')
    _write(outputs / "video" / "final_output.mp4", "fake-v2")
    _write(outputs / "video" / "new_asset.txt", "new-file")
    sm.snapshot(job_id, {"step": 2}, note="v2")

    restored = sm.undo(job_id)
    assert restored == {"step": 1}

    restored_video = (outputs / "video" / "final_output.mp4").read_text(encoding="utf-8")
    assert restored_video == "fake-v1"
    assert not (outputs / "video" / "new_asset.txt").exists()

    remaining = sm.list_versions(job_id)
    assert len(remaining) == 1
    assert read_json(remaining[0]["state_path"]) == {"step": 1}

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict

from shared.utils import read_json, write_json

from .history import History
from .snapshot import Snapshot
from .storage import Storage


class StateManager:
    def __init__(self) -> None:
        self.storage = Storage()

    def _history(self, job_id: str) -> History:
        return History(self.storage.job_dir(job_id) / "history.json")

    def snapshot(self, job_id: str, state: Dict, note: str = "") -> int:
        history = self._history(job_id)
        version = len(history.list_versions()) + 1
        snap = Snapshot.create(version=version, state=state, note=note)
        state_path = self.storage.job_dir(job_id) / f"v_{version}.json"
        write_json(state_path, snap.state)

        # Snapshot generated assets so undo can restore both files and JSON state.
        assets_path = self.storage.assets_dir(job_id, version)
        self._snapshot_outputs(job_id, assets_path)

        history.append(
            {
                "version": version,
                "timestamp": snap.timestamp,
                "note": note,
                "state_path": str(state_path),
                "assets_path": str(assets_path),
            }
        )
        return version

    def latest(self, job_id: str) -> Dict:
        versions = self._history(job_id).list_versions()
        if not versions:
            raise ValueError("No snapshot exists for job.")
        return read_json(versions[-1]["state_path"])

    def undo(self, job_id: str) -> Dict:
        history = self._history(job_id)
        versions = history.list_versions()
        if len(versions) < 2:
            raise ValueError("No previous version to revert to.")
        history.pop()
        prev = history.list_versions()[-1]
        self._restore_outputs(job_id, Path(prev["assets_path"]))
        return read_json(prev["state_path"])

    def list_versions(self, job_id: str):
        return self._history(job_id).list_versions()

    def _snapshot_outputs(self, job_id: str, target_dir: Path) -> None:
        outputs_dir = self.storage.outputs_dir(job_id)
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        if outputs_dir.exists():
            for child in outputs_dir.iterdir():
                dst = target_dir / child.name
                if child.is_dir():
                    shutil.copytree(child, dst)
                else:
                    shutil.copy2(child, dst)

    def _restore_outputs(self, job_id: str, snapshot_dir: Path) -> None:
        outputs_dir = self.storage.outputs_dir(job_id)
        if outputs_dir.exists():
            shutil.rmtree(outputs_dir)
        outputs_dir.mkdir(parents=True, exist_ok=True)
        if snapshot_dir.exists():
            for child in snapshot_dir.iterdir():
                dst = outputs_dir / child.name
                if child.is_dir():
                    shutil.copytree(child, dst)
                else:
                    shutil.copy2(child, dst)

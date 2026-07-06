import sys
import os
sys.path.append(os.path.abspath(os.getcwd()))
from agents.orchestrator.workflow import PipelineWorkflow

job_id = sys.argv[1]

def progress_cb(phase, status, percent, meta):
    print(f"PROGRESS: {phase} {status} {percent} {meta}")

workflow = PipelineWorkflow(progress_cb=progress_cb)
story_spec_path = f"data/outputs/{job_id}/story_spec.json"
timing_manifest_path = f"data/outputs/{job_id}/audio/timing_manifest.json"
master_audio_path = f"data/outputs/{job_id}/audio/master_dialogue.wav"

print('Running audio...')
try:
    workflow.run_audio(job_id, story_spec_path)
    print('Audio done')
except Exception as e:
    print('Audio error:', e)

print('Running video...')
try:
    workflow.run_video(job_id, story_spec_path, timing_manifest_path, master_audio_path)
    print('Video done')
except Exception as e:
    print('Video error:', e)

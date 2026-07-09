from enum import Enum

from shared.utils.cloud import is_cloud_mode


class PhaseName(str, Enum):
    STORY = "story"
    AUDIO = "audio"
    VIDEO = "video"
    EDIT = "edit"
    DONE = "done"
    ERROR = "error"


class EditTarget(str, Enum):
    AUDIO = "audio"
    VIDEO_FRAME = "video_frame"
    VIDEO = "video"
    SCRIPT = "script"


DEFAULT_VIDEO_FPS = 24

# Cloud hosts (Render free = 512 MB) use lower resolution and lighter processing.
if is_cloud_mode():
    DEFAULT_VIDEO_RESOLUTION = (960, 540)
    IMAGE_BG_SIZE = (960, 540)
    IMAGE_CHAR_SIZE = (576, 768)
else:
    DEFAULT_VIDEO_RESOLUTION = (1280, 720)
    IMAGE_BG_SIZE = (1280, 720)
    IMAGE_CHAR_SIZE = (768, 1024)

DEFAULT_TARGET_DURATION_SECONDS = 60
MAX_STORY_REPAIR_ATTEMPTS = 3

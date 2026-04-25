import logging
import select
import subprocess
import time
from typing import Optional

import cv2
import numpy as np

logger = logging.Logger(__file__)

def open_stream_process(uri: str) -> subprocess.Popen:
    proc = subprocess.Popen([
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-fflags", "nobuffer",
        "-flags", "low_delay",
        "-analyzeduration", "0",
        "-probesize", "32",
        "-i", uri,
        "-an",
        "-f", "rawvideo",
        "-pix_fmt", "bgr24",
        "pipe:1"
    ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    return proc

def get_resolution(url: str) -> tuple[int, int]:
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-rtsp_transport", "tcp",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0", url
    ], capture_output=True, text=True, timeout=10)
    w, h = map(int, result.stdout.strip().split(","))
    return w, h

class RealtimeStream:
    def __init__(self, url: str,
                 stream_size: Optional[tuple[int, int]] = None) -> None:
        if stream_size is None:
            logger.debug("No stream size given - probing resolution")
            self._width, self._height = get_resolution(url)

        self._frame_size = self._width * self._height * 3

        logger.debug(f"Frame probed: {self._width}x{self._height}, frame size: {self._frame_size}")
        self._proc = open_stream_process(url)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _read_latest_raw(self):
        raw = self._proc.stdout.read(self._frame_size)
        if len(raw) < self._frame_size:
            return None
        while True:
            r, _, _ = select.select([self._proc.stdout], [], [], 0)
            if not r:
                break
            candidate = self._proc.stdout.read(self._frame_size)
            if len(candidate) < self._frame_size:
                break
            raw = candidate
        return raw

    def read_latest_frame(self) -> Optional[np.ndarray]:
        raw = self._read_latest_raw()
        if raw is None:
            return None
        return np.frombuffer(raw, np.uint8).reshape((self._height, self._width, 3))

    def close(self) -> None:
        self._proc.kill()
        self._proc.wait()


import threading
from typing import List, Optional

import numpy as np

BYTES_PER_SAMPLE = 2  # PCM16 = 2 bytes/sample


class AudioTimeline:
    """
    Buffers raw PCM16 mic audio, tagged by elapsed time since the stream
    started, so methods can later slice out the exact raw samples that a Deepgram
    transcript time range (seconds since connection open) refers to.

    Older audio is trimmed once the buffer exceeds `max_buffer_seconds`, since
    we only need enough history to cover one utterance at a time. This saves space.
    """

    def __init__(self, sample_rate: int, max_buffer_seconds: float = 30.0):
        self.sample_rate = sample_rate
        self.max_buffer_samples = int(max_buffer_seconds * sample_rate)

        self._chunks: List[bytes] = []
        self._buffer_start_sample = 0  # sample index of the start of _chunks[0]
        self._total_samples = 0  # sample index of the end of the buffer
        self._lock = threading.Lock()

    def append(self, chunk: bytes):
        """Add a raw PCM16 chunk (from the mic) to the timeline."""
        with self._lock:
            self._chunks.append(chunk)
            self._total_samples += len(chunk) // BYTES_PER_SAMPLE
            self._trim()

    def _trim(self):
        """Drop the oldest chunks once we're holding more than max_buffer_samples."""
        buffered = self._total_samples - self._buffer_start_sample
        while buffered > self.max_buffer_samples and self._chunks:
            oldest = self._chunks.pop(0)
            n = len(oldest) // BYTES_PER_SAMPLE
            self._buffer_start_sample += n
            buffered -= n

    def slice_seconds(self, start_sec: float, end_sec: float) -> Optional[np.ndarray]:
        """
        Return float32 samples in [-1, 1] for the given time range (seconds
        since the connection opened). Returns None if the range is empty or
        has already been trimmed out of the buffer.
        """
        with self._lock:
            start_sample = int(start_sec * self.sample_rate)
            end_sample = int(end_sec * self.sample_rate)

            # Clamp to what we still have buffered (best effort if the start
            # of a long utterance already got trimmed).
            start_sample = max(start_sample, self._buffer_start_sample)
            end_sample = min(end_sample, self._total_samples)

            if end_sample <= start_sample:
                return None

            raw = b"".join(self._chunks)
            samples = np.frombuffer(raw, dtype=np.int16)

            local_start = start_sample - self._buffer_start_sample
            local_end = end_sample - self._buffer_start_sample

            return samples[local_start:local_end].astype(np.float32) / 32768.0

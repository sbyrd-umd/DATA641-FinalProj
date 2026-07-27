import queue
import threading
import time
import warnings
from typing import Optional

# suppress start up noise from transformers import
warnings.filterwarnings(
    "ignore",
    message=r".*_register_pytree_node*",
    category=FutureWarning,
)

import numpy as np
import torch
from transformers.models.wav2vec2.processing_wav2vec2 import Wav2Vec2Processor

from .model import MODEL_NAME, load_emotion_model
from .scoring import describe

SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 0.01  # Below this RMS value, we consider the audio to be silence


class SentimentAnalyzer:
    """
    Feed raw PCM16 audio chunks (same bytes sent to translator) via .feed().
    Buffers internally and runs inference on a background thread every 'hop_seconds'.
    Calls 'on_result(dict)' every reading.
    """

    def __init__(
        self,
        on_result,
        window_seconds: float = 8.0,
        hop_seconds: float = 8.0,
        sample_rate: int = SAMPLE_RATE,
        device: Optional[str] = None,
    ):
        self.on_result = on_result
        self.window_size = int(window_seconds * sample_rate)
        self.hop_size = int(hop_seconds * sample_rate)
        self.sample_rate = sample_rate
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        print(
            f"[sentiment] loading {MODEL_NAME} on {self.device}"
            f"(First run downloads the checkpoint from HuggingFace. ~650MB)..."
        )

        self.processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)

        loaded = load_emotion_model(MODEL_NAME)  # type: ignore[call-arg]
        self.model = loaded.to(self.device) # type: ignore

        self.model.eval()  # put model in evaluation mode (disables dropout, etc.)

        print("[sentiment] model ready.")

        self._buffer = np.zeros(0, dtype=np.float32)  # holds samples until we have enough for a window
        self._queue: "queue.Queue[np.ndarray]" = queue.Queue()  # audio chunks fed from the main thread
        self._stop_event = threading.Event()  # signals the background thread to stop
        self._worker = threading.Thread(target=self._run, daemon=True)  # processes queued audio chunks
        self._last_label = None  # avoids re-firing on_result for the same label repeatedly

    def start(self):
        """Start the background thread for processing audio."""
        self._worker.start()

    def stop(self):
        """Stop the background thread."""
        self._stop_event.set()

    def feed(self, audio_chunk: np.ndarray):
        """Feed a new audio chunk to the analyzer."""
        samples = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        self._queue.put(samples)

    def _run(self):
        """Background thread that processes audio chunks from the queue and runs inference on them."""
        while not self._stop_event.is_set():
            try:
                chunk = self._queue.get(timeout=0.5)  # wait for a new audio chunk, timeout after 0.5s
            except queue.Empty:
                continue

            self._buffer = np.concatenate([self._buffer, chunk])  # append the new chunk to the buffer

            while len(self._buffer) >= self.window_size:  # enough samples for a window -> run inference
                window = self._buffer[: self.window_size]
                self._buffer = self._buffer[self.hop_size :]  # hop forward

                # If the window isn't silent, run inference. If it is, reset the last
                # label so the next non-silent window will trigger on_result again.
                if not self._is_silent(window):
                    self._infer(window)
                else:
                    self._last_label = None
                    continue

    @staticmethod
    def _is_silent(window: np.ndarray) -> bool:
        """Check if the audio window is silent based on RMS value."""
        rms = float(np.sqrt(np.mean(window**2)))
        return rms < SILENCE_THRESHOLD

    def _infer(self, window: np.ndarray):
        """Run inference on a single audio window."""
        # The processor takes care of resampling, normalization, and padding.
        inputs = self.processor(
            window, sampling_rate=self.sample_rate, return_tensors="pt", padding=True
        )
        input_values = inputs.input_values.to(self.device)

        with torch.no_grad():  # disable gradient calc for inference (saves memory/compute)
            _, logits = self.model(input_values)

        arousal, dominance, valence = logits[0].tolist()

        desc = describe(valence, arousal, dominance)

        result = {
            "timestamp": time.time(),
            "arousal": round(arousal, 3),
            "dominance": round(dominance, 3),
            "valence": round(valence, 3),
            "label": desc["label"],
            "intensity": desc["intensity"],
            "flagged": desc["flagged"],
        }

        if result["label"] != self._last_label:
            self._last_label = result["label"]
            self.on_result(result)

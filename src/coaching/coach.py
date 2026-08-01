import queue
import threading
import time
from collections import deque
from typing import Deque, Dict, List

from .client import OllamaClient
from .prompts import SYSTEM_PROMPT, build_user_prompt


class CoachingEngine:
    """
    Watches (transcript_text, sentiment_result) pairs as they arrive and,
    when a sentiment trigger fires (and we're past cooldown), asks a small
    local LLM for one short coaching note. Runs on a background thread --
    same pattern as SentimentAnalyzer -- so generation never blocks
    transcription or sentiment inference.
    """
    
    def __init__(
        self,
        on_note,
        model: str,
        host: str = "http://localhost:11434",
        buffer_size: int = 8,
        cooldown_seconds: float = 20.0,
        intensity_threshold: float = 0.0,
    ):
        self.on_note = on_note
        self.client = OllamaClient(model=model, host=host)
        self.cooldown_seconds = cooldown_seconds
        self.intensity_threshold = intensity_threshold
        
        self._buffer: Deque[Dict] = deque(maxlen=buffer_size)
        self._queue: "queue.Queue[List[Dict]]" = queue.Queue()
        self._stop_event = threading.Event()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._last_note_time: float = 0.0
        self._lock = threading.Lock()
        
    def start(self):
        """Start the background thread for coaching."""
        self._worker.start()
        
    def stop(self):
        """Stop the background thread for coaching."""
        self._stop_event.set()
        self._worker.join()
        
    def feed(self, text: str, sentiment_result: dict):
        """
        Call once per utterance, after sentiment inference finishes for it.
        Always buffers the turn for context; only queues an LLM call when
        the trigger condition is met.
        """
        
        turn = {
            "text": text,
            "label": sentiment_result["label"],
            "intensity": sentiment_result["intensity"],
            "flagged": sentiment_result["flagged"],
        }
        with self._lock:
            self._buffer.append(turn)
            turns_snapshot = list(self._buffer)
            
        if self._should_trigger(turn):
            self._last_note_time = time.time()  # reserve the slot immediately (avoid duplicate triggers while queued)
            self._queue.put(turns_snapshot)
            
    def _should_trigger(self, turn: Dict) -> bool:
        """
        Determine if the current turn should trigger a coaching note.
        Only fire on a flagged (negative + intense) turn, rate-limited by cooldown.
        """
        
        if not turn["flagged"]:
            return False
        if turn["intensity"] < self.intensity_threshold:
            return False
        if time.time() - self._last_note_time < self.cooldown_seconds:
            return False
        return True
    
    def _run(self):
        """Background thread: pulls buffered turns off the queue and generates a note for each."""
        
        while not self._stop_event.is_set():
            try:
                turns = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            
            try:
                note = self.client.chat(SYSTEM_PROMPT, build_user_prompt(turns))
            except Exception as e:
                note = f"(coach unavailable: {e})"
                
            self.on_note(note)
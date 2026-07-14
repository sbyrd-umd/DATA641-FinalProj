import queue
import threading
import time
import warnings
from typing import Optional

# surpress start up noise from transformers inport
warnings.filterwarnings(
    "ignore",
    message=r".*_register_pytree_node*",
    category=FutureWarning,
)

import numpy as np
import torch
import torch.nn as nn
from transformers.models.wav2vec2.processing_wav2vec2 import Wav2Vec2Processor
from transformers.models.wav2vec2.modeling_wav2vec2 import (
    Wav2Vec2Model,
    Wav2Vec2PreTrainedModel,
)


MODEL_NAME = "audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim"
SAMPLE_RATE = 16000

# Setting the nuetral point and margin for mapping scores
NUETRAL_VALENCE = 0.4
NUETRAL_AROUSAL = 0.4
NUETRAL_DOMINANCE = 0.4
MARGIN = 0.05

SILENCE_THRESHOLD = 0.01  # Below this RMS value, we consider the audio to be silence



# -------------------
# Defining the model |
# -------------------

# We need this head because wav2vec2 is a self supervised model and does not output any labels or scores.
# This adds a small task specific head to the model that outputs 3 scores for arousal, valence and dominance.
# We can fine-tune this for our specific task of emotion prediction / sentiment analysis in the scope of our application.

class RegressionHead(nn.Module):    # regression not classification because scores are continuous [0, 1]
    """Small MLP head that maps pooled wav2vec2 features to 3 scores."""
    
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.dropout = nn.Dropout(config.final_dropout)
        self.out_proj = nn.Linear(config.hidden_size, config.num_labels)

    def forward(self, x):
        x = self.dropout(x)
        x = torch.tanh(self.dense(x))
        x = self.dropout(x)
        return self.out_proj(x)
    

class EmotionModel(Wav2Vec2PreTrainedModel):
    """wav2vec2 model with a regression head for emotion prediction."""

    all_tied_weights_keys = {}  # fix for newer transformers versions
    
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.wav2vec2 = Wav2Vec2Model(config)
        self.classifier = RegressionHead(config)
        self.init_weights()
        
    def forward(self, input_values): 
        outputs = self.wav2vec2(input_values)   # run through the wav2vec2 model to get hidden states
        hidden_states = outputs[0]
        pooled = torch.mean(hidden_states, dim=1)   # average pooling over the time dimension to get a single vector representation of the audio
        logits = self.classifier(pooled)    # run through the regression head to get 3 scores for arousal, valence and dominance
        return pooled, logits


# -----------------------
# Sentiment Descriptions |
# -----------------------

def _bucket(value: float, neutral: float, margin: float) -> str:
    """Bucket the value into 'low', 'neutral' or 'high' based on the neutral value and margin."""
    if value < neutral - margin:
        return "low"
    elif value > neutral + margin:
        return "high"
    else:
        return "neutral"

def describe(valence: float, arousal: float, dominance: float) -> dict:
    """Describe the emotion based on the valence, arousal and dominance scores.
        This is a heuristic that maps the scores to a readable description of the emotion.
    """
    # ORIGINAL TUNING
    # if valence < VALENCE_THRESHOLD and arousal > AROUSAL_THRESHOLD:
    #     return "High intensity negative emotion"
    # elif valence < VALENCE_THRESHOLD:
    #     return "Negative emotion"
    # elif arousal > AROUSAL_THRESHOLD:
    #     return "High intensity positive emotion"
    # else:
    #     return "Calm / Neutral"
    
    
    ## NEW TUNING
    v = _bucket(valence, NUETRAL_VALENCE, MARGIN)
    a = _bucket(arousal, NUETRAL_AROUSAL, MARGIN)
    d = _bucket(dominance, NUETRAL_DOMINANCE, MARGIN)
    
    # distance from the nuetral point
    # Right now we only use this for flagging
    # but it can be very usefull for more detailed emotion capture
    # We can use this to add an extra dimension to the LLM input for better context
    intensity = (
        (valence - NUETRAL_VALENCE) ** 2
        + (arousal - NUETRAL_AROUSAL) ** 2
        + (dominance - NUETRAL_DOMINANCE) ** 2
    ) ** 0.5
    
    # --- Octant mapping ---
    # +V+A+D = Exuberant/Excited      -V+A+D = Hostile/Angry
    # +V-A+D = Relaxed/Content        -V-A+D = Disdainful/Contemptuous
    # +V+A-D = Dependent/Eager        -V+A-D = Anxious/Distressed
    # +V-A-D = Docile/Calm            -V-A-D = Bored/Disengaged
    if v == "high" and a == "high" and d == "high":
        label = "Excited / Enthusiastic"
    elif v == "low" and a == "high" and d == "high":
        label = "Angry / Hostile"
    elif v == "high" and a == "low" and d == "high":
        label = "Relaxed / Content"
    elif v == "low" and a == "low" and d == "high":
        label = "Disdainful / Contemptuous"
    elif v == "high" and a == "high" and d == "low":
        label = "Eager / Enthusiastic (submissive)"
    elif v == "low" and a == "high" and d == "low":
        label = "Distressed / Anxious"
    elif v == "high" and a == "low" and d == "low":
        label = "Calm / Docile"
    elif v == "low" and a == "low" and d == "low":
        label = "Disengaged / Bored"
    else:
        # Any dimension still in the deadzone -> not confident enough
        # to call a full octant, fall back to a 2-axis read.
        if v == "low" and a == "high":
            label = "Negative / Agitated"
        elif v == "low":
            label = "Negative"
        elif a == "high":
            label = "High energy"
        else:
            label = "Calm / Neutral"
            
    # Flag for escalation: anything low-valence with meaningful
    # intensity, regardless of dominance (covers both "angry" and "distressed").
    flagged = v == "low" and intensity > MARGIN

    return {
        "label": label,
        "intensity": round(intensity, 3),
        "flagged": flagged,
    }
    

# -------------------
# Sentiment Analyzer |
# -------------------

class SentimentAnalyzer:
    """
    Feed raw PCM16 audio chunks (same bytes sent to translator) via .feed().
    Buffers internally and runs inferense on a backround thread every 'hop_seconds'.
    Calls 'on_result(dict)' every reading
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
        
        print(f"[sentiment] loading {MODEL_NAME} on {self.device}"
              f"(First run downloads the checkpoint from HuggingFace. ~650MB)...")
        
        self.processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
        
        loaded = EmotionModel.from_pretrained(MODEL_NAME)  # type: ignore[call-arg]
        assert isinstance(loaded, EmotionModel)
        self.model = loaded.to(self.device)
        
        self.model.eval()   # put model in evaluation mode (disables dropout, etc.)
        
        print(f"[sentiment] model ready.")
        
        self._buffer = np.zeros(0, dtype=np.float32)    # buffer to hold audio samples until we have enough for a window
        self._queue: "queue.Queue[np.ndarray]" = queue.Queue()  # queue to hold audio chunks fed from the main thread
        self._stop_event = threading.Event()    # event to signal the background thread to stop
        self._worker = threading.Thread(target=self._run, daemon=True)  # background thread that runs the _run() method to process audio chunks in the queue
        self._last_label = None    # last label to avoid printing the same label multiple times in a row
        
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
                chunk = self._queue.get(timeout=0.5)    # wait for a new audio chunk from the queue, timeout after 0.5 seconds
            except queue.Empty:
                continue
            
            self._buffer = np.concatenate([self._buffer, chunk])    # append the new chunk to the buffer
            
            while len(self._buffer) >= self.window_size:    # while we have enough samples in the buffer for a window, run inference
                window = self._buffer[: self.window_size]   # get the first window_size samples from the buffer
                self._buffer = self._buffer[self.hop_size :]    # remove the first hop_size samples from the buffer (hop forward)
                
                # If the window is not silent, run inference and call on_result with the result
                # If the window is silent, reset the last label so that the next non-silent window will trigger on_result
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
        
        # The processor takes care of resampling, normalization, and padding the audio to the correct length for the model.
        inputs = self.processor(
            window, sampling_rate=self.sample_rate, return_tensors="pt", padding=True
        )
        input_values = inputs.input_values.to(self.device)  # move the input tensor to the same device as the model (CPU or GPU)
        
        with torch.no_grad():   # disable gradient calculation for inference (saves memory and computation)
            _, logits = self.model(input_values)
        
        arousal, dominance, valence = logits[0].tolist()    # convert scores to a list of floats
        
        # collect description and flagged status from the describe function
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
                


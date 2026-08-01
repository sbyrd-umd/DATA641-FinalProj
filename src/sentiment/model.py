from typing import Dict

import torch
import torch.nn as nn
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file as load_safetensors
from transformers import AutoConfig
from transformers.models.wav2vec2.modeling_wav2vec2 import (
    Wav2Vec2Model,
    Wav2Vec2PreTrainedModel,
)

MODEL_NAME = "audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim"

_LEGACY_TO_PARAMETRIZED = {
    "weight_g": "parametrizations.weight.original0",
    "weight_v": "parametrizations.weight.original1",
}

# -------------------
# Defining the model |
# -------------------
#
# We need this head because wav2vec2 is a self supervised model and does not
# output any labels or scores. This adds a small task specific head to the
# model that outputs 3 scores for arousal, valence and dominance. We can
# fine-tune this for our specific task of emotion prediction / sentiment
# analysis in the scope of our application.


class RegressionHead(nn.Module):
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
        outputs = self.wav2vec2(input_values)  # run through the wav2vec2 model to get hidden states
        hidden_states = outputs[0]
        pooled = torch.mean(hidden_states, dim=1)  # average pooling over time -> single vector per clip
        logits = self.classifier(pooled)  # run through the regression head to get 3 scores
        return pooled, logits


# This next section fixes an issue we had pertaining to weight norms within the huggingface model we're using
# The one we're using uses older naming so we have to rename the keys so that the weights
# in that layer don't get randomly reinitialized

def _remap_weight_norm_keys(state_dict: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
    """Rename legacy weight_norm keys (weight_g/weight_v) to the names the
    current, installed PyTorch's parametrized weight_norm expects, so they
    still line up with the live model's parameter names."""
    remapped = {}
    for key, value in state_dict.items():
        new_key = key
        for legacy_suffix, new_suffix in _LEGACY_TO_PARAMETRIZED.items():
            if key.endswith(f".{legacy_suffix}"):
                new_key = key[: -len(legacy_suffix)] + new_suffix
                break
        remapped[new_key] = value
    return remapped
 
 
def load_emotion_model(model_name: str = MODEL_NAME) -> EmotionModel:
    """
    Load EmotionModel from a HuggingFace checkpoint, patching legacy
    weight_norm key names first so the pos_conv_embed layer actually gets
    its pretrained weights instead of getting re-initialized.
    """
    config = AutoConfig.from_pretrained(model_name)
    model = EmotionModel(config)
 
    # Download the raw weights file ourselves so we can rename keys before
    # they're loaded into the model (from_pretrained does this matching
    # internally and would just drop the mismatched keys again).
    try:
        weights_path = hf_hub_download(repo_id=model_name, filename="model.safetensors")
        state_dict = load_safetensors(weights_path)
    except Exception:
        weights_path = hf_hub_download(repo_id=model_name, filename="pytorch_model.bin")
        state_dict = torch.load(weights_path, map_location="cpu")
 
    state_dict = _remap_weight_norm_keys(state_dict)
 
    missing, unexpected = model.load_state_dict(state_dict, strict=False)
    # masked_spec_embed is a training-only buffer (SpecAugment masking) that's
    # expected to be absent from inference checkpoints; anything else missing
    # means a key didn't line up and is worth knowing about.
    real_missing = [k for k in missing if "masked_spec_embed" not in k]
    if real_missing:
        print(f"[sentiment] warning: weights still missing after remap: {real_missing}")
    if unexpected:
        print(f"[sentiment] warning: unexpected keys in checkpoint: {unexpected}")
 
    return model
from pathlib import Path
import torch

from .model import ModelConfig, NanoLM
from .tokenizer import CharTokenizer


def save_checkpoint(path: str | Path, model: NanoLM, tokenizer: CharTokenizer) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    torch.save({"config": model.config.to_dict(), "model": model.state_dict(), "tokenizer": tokenizer.to_dict()}, path)


def load_checkpoint(path: str | Path, device: str = "cpu") -> tuple[NanoLM, CharTokenizer]:
    payload = torch.load(path, map_location=device, weights_only=True)
    model = NanoLM(ModelConfig(**payload["config"]))
    model.load_state_dict(payload["model"])
    return model.to(device).eval(), CharTokenizer.from_dict(payload["tokenizer"])

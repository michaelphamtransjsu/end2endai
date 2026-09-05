import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import torch

from nano_llm.checkpoint import load_checkpoint

app = FastAPI(title="Nano LLM", version="0.1.0")
CHECKPOINT = os.getenv("NANO_LLM_CHECKPOINT", "checkpoints/nano.pt")


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=1000)
    max_new_tokens: int = Field(default=40, ge=1, le=200)
    temperature: float = Field(default=0.8, gt=0, le=3)
    top_k: int = Field(default=10, ge=1, le=1000)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "checkpoint": "ready" if Path(CHECKPOINT).exists() else "missing"}


@app.post("/generate")
def generate(request: GenerateRequest) -> dict[str, str]:
    if not Path(CHECKPOINT).exists():
        raise HTTPException(503, "checkpoint missing; run train.py first")
    model, tokenizer = load_checkpoint(CHECKPOINT)
    try:
        ids = tokenizer.encode(request.prompt)
    except ValueError as error:
        raise HTTPException(400, str(error)) from error
    output = model.generate(torch.tensor([ids]), request.max_new_tokens, request.temperature, request.top_k)
    return {"text": tokenizer.decode(output[0].tolist())}


@app.get("/", response_class=HTMLResponse)
def chat() -> str:
    return Path(__file__).with_name("static").joinpath("index.html").read_text(encoding="utf-8")

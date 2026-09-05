# Model Card: Nano LLM

## Summary

Nano LLM is a tiny decoder-only character transformer for education. Its default configuration has dimension 32, two layers, four heads, and context length 32 during the documented training run. It uses causal scaled dot-product multi-head attention, RoPE, RMSNorm, and SwiGLU.

## Intended use

- Inspecting an understandable PyTorch transformer implementation.
- Local CPU smoke training, generation, and API exercises.
- Demonstrating autoregressive sampling controls.

It is not intended for factual assistance, production, safety-critical decisions, or benchmarking against commercial models.

## Training and evaluation

The model learns next-character prediction with cross-entropy and AdamW from the bundled corpus. Seeds make initialization, batch sampling, and CLI generation reproducible on a fixed software/hardware stack. Tests cover tensor shapes and causal behavior; they do not establish language quality.

## Limitations and risks

The tiny corpus and model cause memorization, incoherent output, repetition, and arbitrary biases. The character vocabulary rejects unseen characters. No safety filtering, factual grounding, privacy mechanism, or robust evaluation is provided. Temperature/top-k alter sampling but do not make outputs reliable. Do not treat generated text as advice.

# CRISP-DM Report

## 1. Business understanding

The goal is a transparent vertical slice showing how a causal language model moves from local text to a browser chat, while remaining fast enough for CPU smoke testing. Success means functional, reproducible plumbing and correctness tests—not conversational quality.

## 2. Data understanding

The bundled synthetic dialogue is deliberately tiny. Inspection shows repeated `User:`/`Bot:` patterns and a restricted character set. It contains no external or personal data. Its size makes memorization likely and evaluation metrics misleading.

## 3. Data preparation

The tokenizer sorts unique characters, maps them to integer IDs, and forms overlapping input/next-token windows at training time. A serialized vocabulary accompanies each checkpoint. No cleaning or augmentation is performed.

## 4. Modeling

The decoder-only PyTorch model uses token embeddings, causal multi-head self-attention, RoPE, pre-RMSNorm residual blocks, SwiGLU, tied output weights, and cross-entropy loss. AdamW performs optimization. Fixed seeds control initialization and sampled window indices.

## 5. Evaluation

Automated tests verify shapes, scalar loss, character round-trip, causal invariance, checkpoint-backed generation, API health, and HTML availability. A short overfit diagnostic compares printed initial/final training losses. No held-out quality, bias, or safety evaluation is claimed.

## 6. Deployment

FastAPI loads a local checkpoint for each generation request and serves a static single-page chat. Inputs have length and sampling bounds. Deployment is local and single-user; model caching, batching, authentication, monitoring, and production hardening are out of scope.

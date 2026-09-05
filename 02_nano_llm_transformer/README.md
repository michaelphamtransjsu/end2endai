# Project 2: Nano LLM Transformer

An educational, decoder-only character language model. It implements causal multi-head self-attention, RMSNorm, rotary position embeddings (RoPE), and a SwiGLU feed-forward network directly in PyTorch. The defaults are intentionally tiny and run on CPU; CUDA and Apple MPS are optional. This is a learning project, not a competitive chatbot.

## Install

Requires Python 3.10+.

```bash
cd 02_nano_llm_transformer
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Train and generate

All randomness is seeded. The checkpoint contains model configuration, weights, and tokenizer vocabulary.

```bash
python train.py --steps 20 --device cpu
python generate.py --checkpoint checkpoints/nano.pt --prompt $'User: hello\nBot:' --tokens 40 --temperature 0.8 --top-k 10
```

For the smallest smoke run: `python train.py --steps 2 --batch-size 2 --seq-len 16 --dim 16 --layers 1 --heads 2 --output /tmp/nano-smoke.pt`. To request an available laptop accelerator, omit `--device` (auto), or pass `--device cuda` / `--device mps`.

## Test

```bash
python -m pytest -q
```

The suite includes model/loss shape, tokenizer, API/UI smoke, and causal-mask tests. The causal test changes future tokens and confirms earlier logits do not change. A tiny-data overfit check can be run reproducibly:

```bash
python train.py --steps 40 --batch-size 4 --seq-len 16 --dim 16 --layers 1 --heads 2 --learning-rate 0.01 --output /tmp/overfit.pt --device cpu
```

Compare the printed first and final losses; stochastic mini-batches make this an educational diagnostic rather than a quality benchmark.

## API and chat UI

Train the default checkpoint, then start the local server:

```bash
python train.py --steps 20 --device cpu
uvicorn app:app --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/generate -H 'Content-Type: application/json' -d '{"prompt":"User: hello\nBot:","max_new_tokens":8,"temperature":0.8,"top_k":10}'
```

Open <http://127.0.0.1:8000/> for the small browser chat interface. Set `NANO_LLM_CHECKPOINT=/path/model.pt` to use another checkpoint. Prompts must only contain characters present in the training corpus.

## Layout

- `nano_llm/model.py`: transformer components and sampling.
- `nano_llm/tokenizer.py`: character tokenizer interface.
- `train.py`, `generate.py`: reproducible command-line workflows.
- `app.py`, `static/index.html`: FastAPI inference and chat UI.
- `data/tiny_corpus.txt`: bundled toy corpus.
- `tests/`: automated smoke and correctness checks.

Generated checkpoints are gitignored. See the model, dataset, CRISP-DM, and final reports for scope and limitations.

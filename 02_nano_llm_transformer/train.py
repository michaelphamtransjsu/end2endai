"""Reproducible next-character training."""

import argparse
import random
from pathlib import Path

import torch

from nano_llm import CharTokenizer, ModelConfig, NanoLM
from nano_llm.checkpoint import save_checkpoint


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/tiny_corpus.txt")
    parser.add_argument("--output", default="checkpoints/nano.pt")
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--seq-len", type=int, default=32)
    parser.add_argument("--dim", type=int, default=32)
    parser.add_argument("--layers", type=int, default=2)
    parser.add_argument("--heads", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=0.003)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda", "mps"])
    args = parser.parse_args()
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = ("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu") if args.device == "auto" else args.device
    text = Path(args.data).read_text(encoding="utf-8")
    tokenizer = CharTokenizer.from_text(text)
    data = torch.tensor(tokenizer.encode(text), dtype=torch.long)
    if len(data) <= args.seq_len:
        raise ValueError("corpus must contain more tokens than seq-len")
    model = NanoLM(ModelConfig(tokenizer.vocab_size, args.dim, args.layers, args.heads, args.seq_len)).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    generator = torch.Generator().manual_seed(args.seed)
    initial_loss = None
    for step in range(1, args.steps + 1):
        starts = torch.randint(len(data) - args.seq_len, (args.batch_size,), generator=generator)
        x = torch.stack([data[i : i + args.seq_len] for i in starts]).to(device)
        y = torch.stack([data[i + 1 : i + args.seq_len + 1] for i in starts]).to(device)
        _, loss = model(x, y)
        initial_loss = loss.item() if initial_loss is None else initial_loss
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        if step == 1 or step == args.steps:
            print(f"step={step} loss={loss.item():.4f}")
    save_checkpoint(args.output, model, tokenizer)
    print(f"device={device} initial_loss={initial_loss:.4f} final_loss={loss.item():.4f} checkpoint={args.output}")


if __name__ == "__main__":
    main()

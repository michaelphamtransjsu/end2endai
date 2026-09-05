import argparse
import torch

from nano_llm.checkpoint import load_checkpoint


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="checkpoints/nano.pt")
    parser.add_argument("--prompt", default="User: hello\nBot:")
    parser.add_argument("--tokens", type=int, default=40)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    torch.manual_seed(args.seed)
    model, tokenizer = load_checkpoint(args.checkpoint)
    tokens = torch.tensor([tokenizer.encode(args.prompt)], dtype=torch.long)
    result = model.generate(tokens, args.tokens, args.temperature, args.top_k)
    print(tokenizer.decode(result[0].tolist()))


if __name__ == "__main__":
    main()

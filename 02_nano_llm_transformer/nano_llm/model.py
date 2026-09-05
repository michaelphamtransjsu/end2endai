"""Small, readable decoder-only Transformer implemented with PyTorch."""

from dataclasses import asdict, dataclass
import math

import torch
from torch import nn
import torch.nn.functional as F


@dataclass
class ModelConfig:
    vocab_size: int
    dim: int = 32
    n_layers: int = 2
    n_heads: int = 4
    max_seq_len: int = 64
    dropout: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(dim))
        self.eps = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps) * self.weight


class RotaryEmbedding(nn.Module):
    def __init__(self, head_dim: int, max_seq_len: int):
        super().__init__()
        if head_dim % 2:
            raise ValueError("head dimension must be even")
        positions = torch.arange(max_seq_len).float()
        inverse = 1.0 / (10000 ** (torch.arange(0, head_dim, 2).float() / head_dim))
        angles = torch.outer(positions, inverse)
        self.register_buffer("cos", angles.cos(), persistent=False)
        self.register_buffer("sin", angles.sin(), persistent=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        length = x.size(-2)
        even, odd = x[..., 0::2], x[..., 1::2]
        cos = self.cos[:length].view(1, 1, length, -1)
        sin = self.sin[:length].view(1, 1, length, -1)
        return torch.stack((even * cos - odd * sin, even * sin + odd * cos), dim=-1).flatten(-2)


class CausalSelfAttention(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        if config.dim % config.n_heads:
            raise ValueError("model dimension must be divisible by number of heads")
        self.n_heads = config.n_heads
        self.head_dim = config.dim // config.n_heads
        self.qkv = nn.Linear(config.dim, 3 * config.dim, bias=False)
        self.out = nn.Linear(config.dim, config.dim, bias=False)
        self.rope = RotaryEmbedding(self.head_dim, config.max_seq_len)
        self.dropout = config.dropout

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, length, width = x.shape
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        reshape = lambda value: value.view(batch, length, self.n_heads, self.head_dim).transpose(1, 2)
        q, k, v = self.rope(reshape(q)), self.rope(reshape(k)), reshape(v)
        # PyTorch's fused implementation applies an upper-triangular causal mask.
        attended = F.scaled_dot_product_attention(q, k, v, dropout_p=self.dropout if self.training else 0.0, is_causal=True)
        return self.out(attended.transpose(1, 2).contiguous().view(batch, length, width))


class SwiGLU(nn.Module):
    def __init__(self, dim: int):
        super().__init__()
        hidden = int(8 * dim / 3)
        self.gate = nn.Linear(dim, hidden, bias=False)
        self.up = nn.Linear(dim, hidden, bias=False)
        self.down = nn.Linear(hidden, dim, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.down(F.silu(self.gate(x)) * self.up(x))


class Block(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.attention_norm = RMSNorm(config.dim)
        self.attention = CausalSelfAttention(config)
        self.ffn_norm = RMSNorm(config.dim)
        self.feed_forward = SwiGLU(config.dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attention(self.attention_norm(x))
        return x + self.feed_forward(self.ffn_norm(x))


class NanoLM(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        self.embedding = nn.Embedding(config.vocab_size, config.dim)
        self.blocks = nn.ModuleList(Block(config) for _ in range(config.n_layers))
        self.norm = RMSNorm(config.dim)
        self.lm_head = nn.Linear(config.dim, config.vocab_size, bias=False)
        self.lm_head.weight = self.embedding.weight

    def forward(self, tokens: torch.Tensor, targets: torch.Tensor | None = None):
        if tokens.size(1) > self.config.max_seq_len:
            raise ValueError("sequence exceeds max_seq_len")
        x = self.embedding(tokens)
        for block in self.blocks:
            x = block(x)
        logits = self.lm_head(self.norm(x))
        loss = None if targets is None else F.cross_entropy(logits.flatten(0, 1), targets.flatten())
        return logits, loss

    @torch.inference_mode()
    def generate(self, tokens: torch.Tensor, max_new_tokens: int, temperature: float = 1.0, top_k: int | None = 20) -> torch.Tensor:
        if temperature <= 0:
            raise ValueError("temperature must be positive")
        for _ in range(max_new_tokens):
            context = tokens[:, -self.config.max_seq_len :]
            logits, _ = self(context)
            logits = logits[:, -1] / temperature
            if top_k is not None and top_k > 0:
                values, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < values[:, [-1]]] = -math.inf
            next_token = torch.multinomial(F.softmax(logits, dim=-1), 1)
            tokens = torch.cat((tokens, next_token), dim=1)
        return tokens

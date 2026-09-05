import torch

from nano_llm.model import ModelConfig, NanoLM


def test_tensor_shapes_and_loss():
    model = NanoLM(ModelConfig(vocab_size=11, dim=16, n_layers=1, n_heads=2, max_seq_len=8))
    tokens = torch.randint(0, 11, (3, 8))
    logits, loss = model(tokens, tokens)
    assert logits.shape == (3, 8, 11)
    assert loss.ndim == 0


def test_attention_is_causal():
    torch.manual_seed(1)
    model = NanoLM(ModelConfig(vocab_size=11, dim=16, n_layers=1, n_heads=2, max_seq_len=6)).eval()
    first = torch.tensor([[1, 2, 3, 4, 5, 6]])
    changed_future = torch.tensor([[1, 2, 3, 9, 8, 7]])
    with torch.no_grad():
        logits_a, _ = model(first)
        logits_b, _ = model(changed_future)
    torch.testing.assert_close(logits_a[:, :3], logits_b[:, :3])


def test_tiny_batch_can_overfit():
    torch.manual_seed(7)
    model = NanoLM(ModelConfig(vocab_size=5, dim=16, n_layers=1, n_heads=2, max_seq_len=8))
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.02)
    inputs = torch.tensor([[0, 1, 2, 3, 4, 0, 1, 2]])
    targets = torch.tensor([[1, 2, 3, 4, 0, 1, 2, 3]])
    _, initial = model(inputs, targets)
    for _ in range(20):
        _, loss = model(inputs, targets)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    _, final = model(inputs, targets)
    assert final.item() < initial.item() * 0.25

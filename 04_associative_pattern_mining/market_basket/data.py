"""Dataset loading and validation."""
from __future__ import annotations

import json
from pathlib import Path


def load_transactions(path: str | Path) -> list[frozenset[str]]:
    """Load JSON baskets and return normalized, de-duplicated transactions."""
    with Path(path).open(encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, list) or not raw:
        raise ValueError("dataset must be a non-empty JSON list")

    transactions: list[frozenset[str]] = []
    for index, basket in enumerate(raw):
        if not isinstance(basket, list) or not basket:
            raise ValueError(f"transaction {index} must be a non-empty list")
        if not all(isinstance(item, str) and item.strip() for item in basket):
            raise ValueError(f"transaction {index} contains a blank or non-string item")
        normalized = frozenset(item.strip().lower() for item in basket)
        transactions.append(normalized)
    return transactions

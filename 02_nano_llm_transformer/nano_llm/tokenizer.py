"""A deliberately simple character tokenizer with a serializable vocabulary."""

from dataclasses import dataclass


@dataclass
class CharTokenizer:
    chars: list[str]

    @classmethod
    def from_text(cls, text: str) -> "CharTokenizer":
        return cls(sorted(set(text)))

    @property
    def vocab_size(self) -> int:
        return len(self.chars)

    def encode(self, text: str) -> list[int]:
        table = {char: index for index, char in enumerate(self.chars)}
        try:
            return [table[char] for char in text]
        except KeyError as error:
            raise ValueError(f"character not in vocabulary: {error.args[0]!r}") from error

    def decode(self, ids: list[int]) -> str:
        return "".join(self.chars[index] for index in ids)

    def to_dict(self) -> dict[str, list[str]]:
        return {"chars": self.chars}

    @classmethod
    def from_dict(cls, value: dict[str, list[str]]) -> "CharTokenizer":
        return cls(value["chars"])

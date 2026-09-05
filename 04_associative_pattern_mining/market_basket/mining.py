"""Small, dependency-free Apriori and association-rule implementation."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Rule:
    antecedent: frozenset[str]
    consequent: frozenset[str]
    support: float
    confidence: float
    lift: float

    def as_dict(self) -> dict:
        return {
            "antecedent": sorted(self.antecedent),
            "consequent": sorted(self.consequent),
            "support": round(self.support, 6),
            "confidence": round(self.confidence, 6),
            "lift": round(self.lift, 6),
        }


def _check_fraction(name: str, value: float) -> None:
    if not 0 < value <= 1:
        raise ValueError(f"{name} must be greater than 0 and at most 1")


def apriori(transactions: list[frozenset[str]], min_support: float) -> dict[frozenset[str], float]:
    """Return all frequent itemsets and their fractional support."""
    _check_fraction("min_support", min_support)
    if not transactions:
        raise ValueError("transactions cannot be empty")
    total = len(transactions)
    items = sorted(set().union(*transactions))
    candidates = {frozenset([item]) for item in items}
    frequent: dict[frozenset[str], float] = {}
    size = 1
    while candidates:
        level: set[frozenset[str]] = set()
        for candidate in candidates:
            support = sum(candidate <= basket for basket in transactions) / total
            if support >= min_support:
                frequent[candidate] = support
                level.add(candidate)
        size += 1
        joined = {left | right for left in level for right in level if len(left | right) == size}
        candidates = {
            candidate for candidate in joined
            if all(frozenset(part) in level for part in combinations(candidate, size - 1))
        }
    return frequent


def association_rules(
    itemsets: dict[frozenset[str], float], min_confidence: float, min_lift: float = 0.0
) -> list[Rule]:
    """Generate rules from frequent itemsets, sorted by recommendation utility."""
    _check_fraction("min_confidence", min_confidence)
    if min_lift < 0:
        raise ValueError("min_lift cannot be negative")
    rules: list[Rule] = []
    for itemset, support in itemsets.items():
        if len(itemset) < 2:
            continue
        for size in range(1, len(itemset)):
            for values in combinations(sorted(itemset), size):
                antecedent = frozenset(values)
                consequent = itemset - antecedent
                confidence = support / itemsets[antecedent]
                lift = confidence / itemsets[consequent]
                if confidence >= min_confidence and lift >= min_lift:
                    rules.append(Rule(antecedent, consequent, support, confidence, lift))
    return sorted(rules, key=lambda rule: (-rule.lift, -rule.confidence, -rule.support, sorted(rule.consequent)))


def recommend(basket: set[str], rules: list[Rule], limit: int = 5) -> list[dict]:
    """Recommend unseen items from rules whose antecedents are in the basket."""
    best: dict[str, Rule] = {}
    for rule in rules:
        if rule.antecedent <= basket:
            for item in rule.consequent - basket:
                current = best.get(item)
                if current is None or (rule.lift, rule.confidence, rule.support) > (current.lift, current.confidence, current.support):
                    best[item] = rule
    ranked = sorted(best.items(), key=lambda pair: (-pair[1].lift, -pair[1].confidence, -pair[1].support, pair[0]))
    return [{"item": item, **rule.as_dict()} for item, rule in ranked[:limit]]

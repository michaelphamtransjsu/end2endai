import json

import pytest

from market_basket.data import load_transactions
from market_basket.mining import apriori, association_rules, recommend


def test_load_normalizes_and_deduplicates(tmp_path):
    path = tmp_path / "baskets.json"
    path.write_text(json.dumps([[" Milk ", "milk", "Bread"]]))
    assert load_transactions(path) == [frozenset({"milk", "bread"})]


def test_load_rejects_invalid_transaction(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps([["milk", ""]]))
    with pytest.raises(ValueError, match="blank"):
        load_transactions(path)


def test_apriori_rule_metrics_and_recommendation():
    baskets = [frozenset({"a", "b"}), frozenset({"a", "b"}), frozenset({"a"}), frozenset({"c"})]
    itemsets = apriori(baskets, 0.25)
    assert itemsets[frozenset({"a", "b"})] == 0.5
    rules = association_rules(itemsets, 0.5)
    rule = next(rule for rule in rules if rule.antecedent == {"b"})
    assert rule.confidence == 1.0
    assert rule.lift == pytest.approx(4 / 3)
    assert recommend({"b"}, rules)[0]["item"] == "a"


@pytest.mark.parametrize("support", [0, 1.1])
def test_apriori_rejects_bad_threshold(support):
    with pytest.raises(ValueError):
        apriori([frozenset({"a"})], support)

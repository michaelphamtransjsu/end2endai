"""Command-line mining pipeline."""
import argparse
import json
from pathlib import Path

from .data import load_transactions
from .mining import apriori, association_rules


def mine(path: str | Path, min_support: float, min_confidence: float, min_lift: float):
    transactions = load_transactions(path)
    itemsets = apriori(transactions, min_support)
    rules = association_rules(itemsets, min_confidence, min_lift)
    return transactions, itemsets, rules


def main() -> None:
    default_data = Path(__file__).parents[1] / "sample_transactions.json"
    parser = argparse.ArgumentParser(description="Mine frequent itemsets and association rules")
    parser.add_argument("--data", default=default_data)
    parser.add_argument("--min-support", type=float, default=0.15)
    parser.add_argument("--min-confidence", type=float, default=0.5)
    parser.add_argument("--min-lift", type=float, default=1.0)
    parser.add_argument("--output", help="optional JSON output path")
    args = parser.parse_args()
    transactions, itemsets, rules = mine(args.data, args.min_support, args.min_confidence, args.min_lift)
    result = {
        "transaction_count": len(transactions),
        "frequent_itemsets": [{"items": sorted(items), "support": round(value, 6)} for items, value in sorted(itemsets.items(), key=lambda pair: (len(pair[0]), sorted(pair[0])))],
        "rules": [rule.as_dict() for rule in rules],
    }
    rendered = json.dumps(result, indent=2)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()

"""Run the complete lab for every bundled dataset."""

import argparse
import json

from skills_lab import DATASETS
from skills_lab.reporting import create_outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()
    for name in DATASETS:
        print(json.dumps({"dataset": name, **create_outputs(name, args.output_dir)}, sort_keys=True))


if __name__ == "__main__":
    main()

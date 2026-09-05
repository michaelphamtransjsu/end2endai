# Dataset Card: Tiny Conversation Corpus

## Description and provenance

`data/tiny_corpus.txt` is a seven-line synthetic English dialogue written for this repository. It contains no scraped, personal, licensed third-party, or sensitive data.

## Purpose and processing

The corpus exists solely to make the full training pipeline run quickly. Text is read as UTF-8 and tokenized into sorted unique characters. Training samples fixed-length, overlapping next-character windows. There are no train/validation/test splits because this is a smoke/overfit exercise, not an empirical quality study.

## Limitations

The dataset is extremely small, repetitive, English-only, and not representative of natural conversations. It cannot support generalization, fairness, safety, or model-quality claims. Its vocabulary also limits accepted prompts to observed characters.

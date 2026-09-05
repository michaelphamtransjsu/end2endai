# Final Report

## Delivered scope

The project provides a pure-PyTorch tiny causal transformer, character tokenizer, bundled synthetic corpus, deterministic trainer/checkpoint workflow, sampling CLI, FastAPI endpoint, browser interface, tests, and documentation. The default deliberately favors short CPU execution over output quality.

## Verification record

Verification was performed on 2026-09-01. Exact commands and observed results are recorded below after the final run.

- `python -m pip install -r requirements.txt` completed successfully. It installed PyTorch 2.13.0+cu130, FastAPI 0.141.1, and pytest 8.4.2 in the supplied Python 3.14 environment.
- `python train.py --steps 2 --batch-size 2 --seq-len 16 --dim 16 --layers 1 --heads 2 --output /tmp/nano-smoke.pt --device cpu` completed on CPU. Printed loss was 14.1186 at step 1 and 13.9639 at step 2; `/tmp/nano-smoke.pt` was created outside the repository.
- `python generate.py --checkpoint /tmp/nano-smoke.pt --prompt $'User: hello\nBot:' --tokens 8 --temperature 0.8 --top-k 10` completed and printed the prompt followed by eight colon characters. This confirms plumbing, not output quality.
- `python train.py --steps 40 --batch-size 4 --seq-len 16 --dim 16 --layers 1 --heads 2 --learning-rate 0.01 --output /tmp/overfit.pt --device cpu` completed. Printed loss was 14.1210 at step 1 and 2.1908 at step 40. Different sampled batches mean the values are a diagnostic, not directly comparable evaluation measurements.
- With `NANO_LLM_CHECKPOINT=/tmp/nano-smoke.pt uvicorn app:app --host 127.0.0.1 --port 8765`, `curl -fsS http://127.0.0.1:8765/health` returned HTTP 200 and `{"status":"ok","checkpoint":"ready"}`. A generation POST returned HTTP 200 and text, and an HTML assertion found the title and temperature control, smoke-testing the chat interface.
- `python -m pytest -q` reported 5 passed and 2 warnings in 4.01 seconds. This includes the automated fixed-batch overfit assertion, tensor shapes, causal masking, tokenizer, checkpoint-backed API, and chat HTML tests.

PyTorch emitted a warning that NumPy was absent; NumPy is not needed by this project. FastAPI also emitted a TestClient deprecation warning concerning the future `httpx2` package. Neither warning caused a failure.

## Final release audit

The release audit was repeated on 2026-09-01 from `02_nano_llm_transformer` using the README workflow:

- `python -m pip install --no-cache-dir -r requirements.txt` completed successfully, followed by `python -m pip check`, which printed `No broken requirements found`. Import verification reported PyTorch `2.13.0+cu130`, FastAPI `0.141.1`, Uvicorn `0.52.4`, pytest `8.4.2`, and HTTPX `0.28.1` under Python 3.14.4.
- An initial attempt to use the optional PyTorch CPU wheel index, `python -m pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu`, failed because the audit environment's network tunnel returned HTTP 403. This was an environment-specific installation attempt not present in the README; using the documented `requirements.txt` command succeeded, so no dependency-file fix was required.
- `python train.py --steps 20 --device cpu` completed with step-1 loss `30.1549` and step-20 loss `3.6470`, writing the ignored `checkpoints/nano.pt` artifact. The artifact was removed after verification.
- `python generate.py --checkpoint checkpoints/nano.pt --prompt $'User: hello\nBot:' --tokens 40 --temperature 0.8 --top-k 10` completed and produced 40 sampled characters after the prompt. As expected for the toy corpus, the text was repetitive and incoherent.
- `python -m pytest -q` reported `5 passed, 2 warnings in 5.25s`. The warnings were the same optional NumPy and TestClient deprecation notices described above.
- `uvicorn app:app --host 127.0.0.1 --port 8000` started successfully. `curl -fsS http://127.0.0.1:8000/health` returned `{"status":"ok","checkpoint":"ready"}`, and the documented generation POST returned HTTP 200 with generated text.
- The frontend is a static HTML file and therefore has no compilation/build step. `curl -fsS http://127.0.0.1:8000/` followed by an assertion for the title, temperature control, top-k control, and generation script passed, confirming that FastAPI serves the interface assets used by the browser.
- The README's install, training, generation, test, server, health, and generation-request commands were compared to the implemented CLI arguments and routes and then executed as above. No command mismatch or critical end-to-end code defect was found, so this audit intentionally adds no feature or implementation change.
- After removing `checkpoints/`, `.pytest_cache/`, and Python bytecode caches, `git diff --check` passed. A scan found no likely credential assignments, no files larger than 1 MiB, and no generated checkpoint, cache, virtual environment, `node_modules`, or build directory in the change set. Only this report changed during the audit.

## Limitations

- This model is a pedagogical toy and is not comparable to commercial LLMs.
- Tiny-data memorization is expected; generated text is generally poor and untrustworthy.
- The character tokenizer cannot encode characters absent from training.
- Determinism across different PyTorch versions/devices is not guaranteed.
- The API reloads the checkpoint per request and has no production security or concurrency design.
- No quality, safety, fairness, latency, or throughput benchmark is claimed.

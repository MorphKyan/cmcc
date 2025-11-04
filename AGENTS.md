# Repository Guidelines
## Project Structure & Module Organization
Runtime code lives in `src/`: `core/` wires shared dependencies and lifecycle hooks, `module/` contains ASR, VAD, RAG, and LLM adapters, `services/audio_pipeline.py` handles streaming orchestration, and `api/` exposes FastAPI endpoints backed by `run_api.py`. Configuration defaults reside in `src/config/config.py` and `logging_config.py`. Real-time entrypoints are `main.py` for the console loop and `run_api.py` for API-only deployments. Knowledge sources sit in `data/` (commit CSVs) while `chroma_db/` is derived and may be rebuilt locally; UI experiments live in `frontend/vue-project`. Tests follow the `test_*.py` pattern in the repo root, so add new suites alongside related streaming scenarios.

## Build, Test, and Development Commands
Work in Python >=3.8. Set up dependencies with `python -m venv .venv && .\.venv\Scripts\activate` then `pip install -r requirements.txt`. Run the integrated voice agent via `python main.py --device cpu` (switch to `--device cuda:0` for GPU validation). Launch the REST service using `python run_api.py` or `uvicorn src.api.rag_api:app --reload --port 5000`. Execute regressions with `python -m pytest -q`; focus on a single path through `python -m pytest test_real_streaming.py -k decoder`.

## Coding Style & Naming Conventions
Follow PEP 8 with four-space indentation, `snake_case` modules/functions, and `CamelCase` classes. Mirror existing docstring language - most pipelines use concise Chinese summaries; keep additions consistent or provide a bilingual update. Add type hints on new public functions, prefer explicit return types, and centralise configuration through `src/config/config.py`. Use `loguru.logger` for diagnostics and keep info-level messages actionable.

## Testing Guidelines
Leverage `pytest`; name files `test_<feature>.py` and functions `def test_<behavior>()`. Align new cases with the existing streaming decoder matrix by asserting both transcript accuracy and timing/sequence checks. When modifying RAG or data loading, craft fixtures under the same directory and clean up any temporary ChromaDB state before assertions. Run `python -m pytest --maxfail=1 --disable-warnings -q` before submitting and capture the command in your PR description.

## Commit & Pull Request Guidelines
History uses terse, imperative subjects (`fix api`, `decoder`), so keep messages under ~65 characters and describe the outcome, not the implementation. Squash exploratory commits prior to review. A PR should include: a short summary, affected modules or scripts, the exact commands used for testing, and any sample JSON/audio artefacts needed for validation. Reference linked issues and call out configuration or data refresh steps (e.g., needing `--force-rag-reload`) so deployers can reproduce updates.

## Configuration & Data Hygiene
Store API keys and device secrets as environment variables read inside `src/config/config.py`; never hard-code credentials. Treat `data/` as the single source of truth for knowledge - update CSVs, then rebuild embeddings with `python main.py --force-rag-reload` before packaging changes. Generated assets (`chroma_db/`, recordings, caches) stay out of version control per `.gitignore`; attach only the excerpts reviewers require.

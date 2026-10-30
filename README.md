# Multi-Agent AI Analyst

AI/ML engineering project by Otabek Boymirzayev. A FastAPI backend coordinates business-data, document-retrieval and bounded arithmetic agents; a React interface displays the answer and agent path.

The application lives in [`Desktop/multi agent rag`](Desktop/multi%20agent%20rag). Use that directory as the API deployment root, and its `frontend` directory for the frontend build.

## Official Gemini setup

Read [GEMINI_SETUP.md](Desktop/multi%20agent%20rag/GEMINI_SETUP.md). Configure a direct Google AI Studio key as `GOOGLE_API_KEY` on the backend. The former proxy token and proxy URL are no longer used. Keep provider keys out of the frontend and Git.

From the application directory:

```sh
python -m pip install -r requirements.txt
python -m src.ingest
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Ingestion sends sample document text to Google and creates a separate model/version-specific index. Previous indexes are preserved. Live answers require a valid key and available quota; SQL questions use the bundled sample database.

Tests: `python -m pytest tests/test_api_contract.py tests/test_safe_tools.py tests/test_google_provider.py -q`.

See [deployment notes](Desktop/multi%20agent%20rag/DEPLOYMENT.md) for frontend origin and hosting configuration.

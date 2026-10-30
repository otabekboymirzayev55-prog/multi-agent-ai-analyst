# Deployment and verification
Author: Otabek Boymirzayev — AI/ML Engineer.

The repository root contains `Desktop/multi agent rag`. Configure this exact directory as the Render API root, and its `frontend` subdirectory as the frontend root. The Blueprint sets the API root explicitly. Configure GOOGLE_API_KEY with a direct Google AI Studio key. Optional GOOGLE_CHAT_MODEL and GOOGLE_EMBED_MODEL select the official Gemini models. The old proxy credentials are ignored. Never place provider keys in VITE_ variables.

Install Python requirements, confirm data/company.db exists, and run `python -m src.ingest` to build the document index with the same embedding model used for retrieval. The bundled database is sample data. Do not use it as a production customer store.

The frontend uses VITE_API_URL (base URL without /chat). Configure ALLOWED_ORIGINS with the deployed frontend origin. Build with `npm install && npm run build` and publish dist. `/health` only checks process/configuration, not provider credit or model availability. Verify POST /chat separately after deployment.

Each browser tab sends X-Session-ID. Chat history is bounded, process-local and disappears on restart. API failures return 503; a concurrent request returns 429. Arithmetic supports bounded expressions, not general Python. SQL executes against a read-only SQLite connection. Public access should be placed behind your hosting provider's rate controls before broad distribution.

For official Gemini setup and index migration see GEMINI_SETUP.md.

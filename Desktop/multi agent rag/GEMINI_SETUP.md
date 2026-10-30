# Official Gemini setup

The backend uses https://generativelanguage.googleapis.com/v1beta/openai/ through the existing LangChain clients. It no longer calls the former class proxy.

Set a direct Google AI Studio key as `GOOGLE_API_KEY` in `.env` locally and in the Render service's secret environment. Obtain it at https://aistudio.google.com/api-keys. Never copy the old proxy token into this variable. Do not put a provider key in the frontend or commit `.env`.

Defaults: `GOOGLE_CHAT_MODEL=gemini-3.5-flash-lite`, `GOOGLE_EMBED_MODEL=gemini-embedding-001`, `GOOGLE_INDEX_VERSION=v1`. Former GEMINI_API_KEY, PROXY_BASE_URL and proxy model settings are ignored. `/health` reports whether the direct key is configured; it does not prove that the key has available quota.

Run `python -m src.ingest` once after adding the key. The sample documents are sent to Google for embedding. A new model/version-specific local Qdrant path is used. Existing proxy indexes are not deleted or queried. For updated documents, increment GOOGLE_INDEX_VERSION and ingest again. A host with ephemeral storage must retain or rebuild this new index when deploying; SQL-only questions do not require the document index.

Restart the API, then verify a real `/chat` question. The frontend requires no provider credential changes. Deploy the backend with the same Google variables and index before declaring the AI demo operational.

Official reference: https://ai.google.dev/gemini-api/docs/openai.

## Windows local launch

After configuring `.env`, installing dependencies and building the Google index, run `./start.ps1` from this folder. It starts background processes and stores logs under ignored `.run/`. Never upload `.env` or your private index. These localhost URLs are available only while this computer and the processes are running. Render uses its own secret settings; local `.env` is not transferred automatically.

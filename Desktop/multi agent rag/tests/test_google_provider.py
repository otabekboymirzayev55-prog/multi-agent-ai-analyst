from pathlib import Path
from unittest.mock import Mock
import pytest
from src import config
from src import llm

def test_only_direct_google_key_is_used(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY', 'old-proxy-token')
    monkeypatch.setattr(config, 'GOOGLE_API_KEY', None)
    with pytest.raises(RuntimeError, match='GOOGLE_API_KEY'):
        llm.create_chat_model()

def test_health_does_not_treat_proxy_key_as_google_key(monkeypatch):
    from fastapi.testclient import TestClient
    from api.main import app
    monkeypatch.setenv('GEMINI_API_KEY', 'old-proxy-token')
    monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
    response = TestClient(app).get('/health')
    assert response.json()['configured'] is False
    assert response.json()['provider'] == 'google-gemini'

def test_chat_client_uses_official_endpoint(monkeypatch):
    monkeypatch.setattr(config, 'GOOGLE_API_KEY', 'test-google-key')
    client = llm.create_chat_model()
    assert client.openai_api_base == 'https://generativelanguage.googleapis.com/v1beta/openai/'
    assert client.model_name == 'gemini-3.5-flash-lite'

def test_embeddings_send_text_not_openai_token_ids(monkeypatch):
    monkeypatch.setattr(config, 'GOOGLE_API_KEY', 'test-google-key')
    client = llm.create_embeddings()
    fake = Mock()
    fake.create.return_value = {'data':[{'embedding':[0.1, 0.2]}]}
    client.client = fake
    assert client.embed_documents(['O‘zbekcha matn']) == [[0.1,0.2]]
    assert isinstance(fake.create.call_args.kwargs['input'][0], str)
    assert fake.create.call_args.kwargs['model'] == 'gemini-embedding-001'
    assert fake.create.call_args.kwargs['encoding_format'] == 'float'
    assert client.check_embedding_ctx_length is False

def test_new_google_index_does_not_reuse_proxy_store():
    assert 'qdrant_google_gemini_embedding_001' in config.VECTOR_DB_PATH
    assert config.COLLECTION_NAME.startswith('company_docs_google_')

def test_existing_index_is_not_deleted(tmp_path, monkeypatch):
    from src import ingest
    existing = tmp_path / 'existing-index'
    existing.mkdir()
    sentinel = existing / 'keep.txt'
    sentinel.write_text('keep')
    monkeypatch.setattr(ingest, 'VECTOR_DB_PATH', str(existing))
    with pytest.raises(RuntimeError, match='already exists'):
        ingest.main()
    assert sentinel.read_text() == 'keep'

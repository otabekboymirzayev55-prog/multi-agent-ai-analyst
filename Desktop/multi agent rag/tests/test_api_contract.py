from fastapi.testclient import TestClient
import api.main as service

class FakeGraph:
    def invoke(self, state, config):
        return {'answer': 'answer for ' + state['question'], 'steps': ['test']}

def test_sessions_do_not_share_history(monkeypatch):
    monkeypatch.setattr(service, 'get_graph', lambda: FakeGraph())
    service.histories.clear()
    client = TestClient(service.app)
    first = 'a' * 32
    second = 'b' * 32
    r = client.post('/chat', headers={'X-Session-ID': first}, json={'question': 'revenue'})
    assert r.status_code == 200
    assert client.get('/history', headers={'X-Session-ID': first}).json()['count'] == 2
    assert client.get('/history', headers={'X-Session-ID': second}).json()['count'] == 0
    assert client.get('/history').json()['count'] == 0

def test_blank_question_and_provider_failure(monkeypatch):
    client = TestClient(service.app)
    assert client.post('/chat', json={'question': '  '}).status_code == 422
    def fail():
        raise RuntimeError('private provider details')
    monkeypatch.setattr(service, 'get_graph', fail)
    result = client.post('/chat', json={'question':'test'})
    assert result.status_code == 503
    assert 'private' not in result.text

def test_busy_request():
    client = TestClient(service.app)
    service.busy.acquire()
    try:
        assert client.post('/chat', json={'question':'test'}).status_code == 429
    finally:
        service.busy.release()

def test_cors_for_frontend():
    client = TestClient(service.app)
    response = client.options('/chat', headers={'Origin':'https://multi-agent-ai-analyst-ui.onrender.com','Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type,x-session-id'})
    assert response.status_code == 200

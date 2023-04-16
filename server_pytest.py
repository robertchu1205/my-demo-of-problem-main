from server import app
import pytest

@pytest.fixture
def client():
  with app.test_client() as client:
    yield client

def test_root(client):
  response = client.get('/')
  assert response.status_code == 200
  # assert response.json['version'] == '0.1.0'

def test_health(client):
  response = client.get('/health')
  assert response.status_code == 200
  assert response.json == {'status': True}

def test_metrics(client):
  response = client.get('/metrics')
  assert response.status_code == 200

def test_history(client):
  response = client.get('/v1/history')
  assert response.status_code == 200
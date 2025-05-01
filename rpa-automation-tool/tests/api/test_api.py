import pytest
from rpa_automation_tool.src.app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_projects(client):
    rv = client.get('/api/projects')
    assert rv.status_code == 200
    assert isinstance(json.loads(rv.data), list)

def test_run_tests(client):
    rv = client.get('/api/run')
    assert rv.status_code == 200
#tests/api/test_api.py
def test_example():
    print("test ran")
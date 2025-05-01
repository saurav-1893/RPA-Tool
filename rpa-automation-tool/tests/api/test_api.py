import pytest
from rpa_automation_tool.src.app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_project_lifecycle(client):
    # Test getting initial projects (should be empty)
    rv = client.get('/api/projects')
    assert rv.status_code == 200
    assert isinstance(json.loads(rv.data), list)
    assert len(json.loads(rv.data)) == 0

    # Test creating a new project
    new_project_data = {"name": "My Test Project"}
    rv = client.post('/api/projects', json=new_project_data)
    assert rv.status_code == 201
    project_data = json.loads(rv.data)
    assert project_data['name'] == "My Test Project"
    assert 'id' in project_data
    project_id = project_data['id']

    # Test getting the newly created project
    rv = client.get(f'/api/projects/{project_id}')
    assert rv.status_code == 200
    assert json.loads(rv.data)['name'] == "My Test Project"

    # Test creating a new test suite within the project
    new_suite_data = {"name": "My Test Suite"}
    rv = client.post(f'/api/projects/{project_id}/suites', json=new_suite_data)
    assert rv.status_code == 201
    suite_data = json.loads(rv.data)
    assert suite_data['name'] == "My Test Suite"
    assert 'id' in suite_data
    suite_id = suite_data['id']

    # Test getting the newly created test suite
    rv = client.get(f'/api/projects/{project_id}/suites/{suite_id}')
    assert rv.status_code == 200
    assert json.loads(rv.data)['name'] == "My Test Suite"

    # Test creating a new test within the test suite
    new_test_data = {"name": "My First Test"}
    rv = client.post(f'/api/projects/{project_id}/suites/{suite_id}/tests', json=new_test_data)
    assert rv.status_code == 201
    test_data = json.loads(rv.data)
    assert test_data['name'] == "My First Test"
    assert 'id' in test_data
    test_id = test_data['id']

    # Test getting the newly created test
    rv = client.get(f'/api/projects/{project_id}/suites/{suite_id}/tests/{test_id}')
    assert rv.status_code == 200
    assert json.loads(rv.data)['name'] == "My First Test"

def test_run_tests(client):
    rv = client.get('/api/run')
    assert rv.status_code == 200
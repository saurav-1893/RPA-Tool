import pytest
from src.app import app
import json


@pytest.fixture(autouse=True)
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_project_lifecycle(client):
    # Test getting initial projects (should be empty)
    rv = client.delete('/api/projects')
    assert rv.status_code == 200

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

    # Test getting all projects (should have one project)
    rv = client.get('/api/projects') # Use the API route
    assert rv.status_code == 200
    projects = json.loads(rv.data)
    assert len(projects) == 1
    assert projects[0]['name'] == "My Test Project"
    assert len(projects[0]['test_suites']) == 1
    assert projects[0]['test_suites'][0]['name'] == "My Test Suite"
    assert len(projects[0]['test_suites'][0]['tests']) == 1
    assert projects[0]['test_suites'][0]['tests'][0]['name'] == "My First Test"

    # Test creating another project
    new_project_data_2 = {"name": "Another Project"}
    rv = client.post('/api/projects', json=new_project_data_2)
    assert rv.status_code == 201

    # Test getting all projects again (should have two projects)
    rv = client.get('/api/projects')
    assert rv.status_code == 200
    projects = json.loads(rv.data)
    assert len(projects) == 2

def test_run_project_tests(client):
    # This test assumes a project named "My Test Project" with a test exists from test_project_lifecycle
    project_name_to_run = "My Test Project"
    # Get the project_id first
    rv = client.get('/api/projects')
    projects = json.loads(rv.data)
    project_to_run = next((p for p in projects if p['name'] == project_name_to_run), None)
    assert project_to_run is not None
    project_id_to_run = project_to_run['id']

    rv = client.post(f'/api/projects/{project_id_to_run}/run')
    assert rv.status_code == 200 # Check if the request was successful
    # Further assertions can be added here to check the results of the run if the API returned them

def test_run_single_test(client):
    # This test assumes a project and test exist from test_project_lifecycle
    project_name = "My Test Project"
    suite_name = "My Test Suite"
    test_name = "My First Test"

    # Get the project, suite, and test IDs
    rv = client.get('/api/projects')
    projects = json.loads(rv.data)
    project = next((p for p in projects if p['name'] == project_name), None)
    assert project is not None
    suite = next((s for s in project['test_suites'] if s['name'] == suite_name), None)
    assert suite is not None
    test = next((t for t in suite['tests'] if t['name'] == test_name), None)
    assert test is not None

    project_id = project['id']
    suite_id = suite['id']
    test_id = test['id']

    rv = client.post(f'/api/projects/{project_id}/suites/{suite_id}/tests/{test_id}/run')
    assert rv.status_code == 200 # Check if the request was successful
    # Further assertions can be added here

def test_record_test(client):
    # This test assumes a project, suite, and test exist from test_project_lifecycle
    project_name = "My Test Project"
    suite_name = "My Test Suite"
    test_name = "My First Test"

    # Get the test ID
    rv = client.get('/api/projects')
    projects = json.loads(rv.data)
    project = next((p for p in projects if p['name'] == project_name), None)
    assert project is not None
    suite = next((s for s in project['test_suites'] if s['name'] == suite_name), None)
    assert suite is not None
    test = next((t for t in suite['tests'] if t['name'] == test_name), None)
    assert test is not None

    project_id = project['id']
    suite_id = suite['id']
    test_id = test['id']

    # Start recording
    rv = client.post(f'/api/projects/{project_id}/suites/{suite_id}/tests/{test_id}/record/start')
    assert rv.status_code == 200 # Check if the request was successful
    assert json.loads(rv.data).get('message') is not None # Check if a message is returned

    # Stop recording
    rv = client.post(f'/api/projects/{project_id}/suites/{suite_id}/tests/{test_id}/record/stop')
    assert rv.status_code == 200 # Check if the request was successful
    assert json.loads(rv.data).get('steps_recorded') is not None # Check if the number of steps recorded is returned

def test_delete_all_projects(client):
    # This test should run last to clean up
    rv = client.delete('/api/projects')
    assert rv.status_code == 200
    rv = client.get('/api/projects')
    assert len(json.loads(rv.data)) == 0
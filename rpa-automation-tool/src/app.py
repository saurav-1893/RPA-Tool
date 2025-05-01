from flask import Flask, jsonify, request
from models.project import Project
from models.test import Test
from models.step import Step
from models.test_suite import TestSuite
from utils.data import load_projects, save_projects, projects_data
from utils.utils import find_project_by_id, find_suite_by_id, find_test_by_id
from core.runner import Runner

app = Flask(__name__)

projects = load_projects()

@app.route("/")
def main():
    return "RPA Automation Tool"

@app.route('/api/projects', methods=['GET'])
def get_all_projects():
    return jsonify([p.__dict__ for p in projects])

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Project name is required'}), 400
    new_project = Project(name=name)
    projects.append(new_project)
    save_projects(projects)
    return jsonify(new_project.__dict__), 201
@app.route('/api/run', methods=['POST'])
def run_all_tests():
    runner = Runner()
    results = runner.run(projects)
    save_projects(projects)
    return jsonify(results)

@app.route('/api/projects/<project_id>/suites', methods=['GET'])
def get_suites(project_id):
    project = find_project_by_id(projects, project_id)
    if project is None:
        return jsonify({'error': 'Project not found'}), 404
    return jsonify([s.__dict__ for s in project.test_suites])

@app.route('/api/projects/<project_id>/suites', methods=['POST'])
def create_suite(project_id):
    project = find_project_by_id(projects, project_id)
    if project is None:
        return jsonify({'error': 'Project not found'}), 404

    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Suite name is required'}), 400

    new_suite = TestSuite(name=name)
    project.test_suites.append(new_suite)
    save_projects(projects)
    return jsonify(new_suite.__dict__), 201

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests', methods=['GET'])
def get_tests(project_id, suite_id):
    project = find_project_by_id(projects, project_id)
    if project is None:
        return jsonify({'error': 'Project not found'}), 404

    suite = find_suite_by_id(project.test_suites, suite_id)
    if suite is None:
        return jsonify({'error': 'Test Suite not found'}), 404

    return jsonify([t.__dict__ for t in suite.tests])

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests', methods=['POST'])
def create_test(project_id, suite_id):
    project = find_project_by_id(projects, project_id)
    if project is None:
        return jsonify({'error': 'Project not found'}), 404

    suite = find_suite_by_id(project.test_suites, suite_id)
    if suite is None:
        return jsonify({'error': 'Test Suite not found'}), 404

    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Test name is required'}), 400

    new_test = Test(name=name)
    suite.tests.append(new_test)
    save_projects(projects)
    return jsonify(new_test.__dict__), 201

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>', methods=['GET'])
def get_test(project_id, suite_id, test_id):
    project = find_project_by_id(projects, project_id)
    if project is None:
        return jsonify({'error': 'Project not found'}), 404
    suite = find_suite_by_id(project.test_suites, suite_id)
    if suite is None:
        return jsonify({'error': 'Test Suite not found'}), 404
    test = find_test_by_id(suite.tests, test_id)
    if test is None:
        return jsonify({'error': 'Test not found'}), 404
    return jsonify(test.__dict__)

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>/record/start', methods=['POST'])
def start_test_recording(project_id, suite_id, test_id):
 project = find_project_by_id(projects_data, project_id)
 if project is None:
 return jsonify({'error': 'Project not found'}), 404
 suite = find_suite_by_id(project.test_suites, suite_id)
 if suite is None:
 return jsonify({'error': 'Test Suite not found'}), 404
 test = find_test_by_id(suite.tests, test_id)
 if test is None:
 return jsonify({'error': 'Test not found'}), 404

 if test.is_recording:
 return jsonify({'message': 'Recording already in progress for this test'}), 409

 test.start_recording()
 save_projects(projects_data)
 return jsonify({'message': f'Recording started for test: {test.name}'})

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>/record/stop', methods=['POST'])
def stop_test_recording(project_id, suite_id, test_id):
 project = find_project_by_id(projects_data, project_id)
 if project is None:
 return jsonify({'error': 'Project not found'}), 404
 suite = find_suite_by_id(project.test_suites, suite_id)
 if suite is None:
 return jsonify({'error': 'Test Suite not found'}), 404
 test = find_test_by_id(suite.tests, test_id)
 if test is None:
 return jsonify({'error': 'Test not found'}), 404
 steps = test.stop_recording()
 save_projects(projects_data)
 return jsonify({'message': f'Recording stopped for test: {test.name}', 'steps_recorded': len(steps)})

if __name__ == "__main__":
    app.run(debug=True)
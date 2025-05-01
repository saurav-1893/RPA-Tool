from flask import Flask, jsonify, request
from flask import render_template
from core.recorder import Recorder
from utils.project_manager import ProjectManager, Runner, save_projects

app = Flask(__name__)

recorder = Recorder()
project_manager = ProjectManager()
projects = project_manager.get_all_projects()

@app.route("/")
def main():
    projects = project_manager.get_all_projects()
    return render_template('index.html')

@app.route('/project/<project_id>')
def project_detail(project_id):
    project = project_manager.get_project(project_id)
    if project is None:
        return jsonify({'error': 'Project not found'}), 404

    return render_template('project.html', project=project)

@app.route('/api/projects', methods=['GET'])
def get_all_projects():
    projects = project_manager.get_all_projects()
    return jsonify([p.__dict__ for p in projects])

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Project name is required'}), 400
    new_project = project_manager.create_project(name)
    return jsonify(new_project.__dict__), 201

@app.route('/api/run', methods=['POST'])
def run_all_tests():
    runner = Runner()
    results = runner.run(projects)
    save_projects(projects)
    return jsonify(results)

@app.route('/api/projects/<project_id>/suites', methods=['GET'])
def get_suites(project_id):
    project = project_manager.get_project(project_id)
    if project is None:
        return jsonify({'error': 'Project not found'}), 404 # Should be 404
    return jsonify([s.__dict__ for s in project.test_suites])

@app.route('/api/projects/<project_id>/suites', methods=['POST'])
def create_suite(project_id):
    project = project_manager.get_project(project_id)
    if project is None:
        return jsonify({'error': 'Project not found'}), 404

    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Suite name is required'}), 400

    test_suite = project_manager.create_test_suite(project_id, name)
    return jsonify(test_suite.__dict__), 201

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests', methods=['GET'])
def get_tests(project_id, suite_id):
    project = project_manager.get_project(project_id)
    if project is None:
        return jsonify({'error': 'Project not found'}), 404
    return jsonify([t.__dict__ for t in suite.tests])

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests', methods=['POST'])
def create_test(project_id, suite_id):
    project = project_manager.get_project(project_id)
    if project is None:
        return jsonify({'error': 'Project not found'}), 404

    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Test name is required'}), 400

    test = project_manager.create_test(project_id, suite_id, name)
    return jsonify(test.__dict__), 201
 
@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>', methods=['GET'])
def get_test(project_id, suite_id, test_id):
    # TODO: update to use the project manager
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
def start_test_recording(project_id, suite_id, test_id): # Remove recorder.start_recording(test) and project_manager.save() and use project_manager.start_recording(project_id, suite_id, test_id)
 
 test = project_manager.start_recording(project_id, suite_id, test_id)

 test = find_test_by_id(suite.tests, test_id)
 if test is None:
 return jsonify({'error': 'Test not found'}), 404

 if test.is_recording:
 return jsonify({'message': 'Recording already in progress for this test'}), 409

 return jsonify({'message': f'Recording started for test: {test.name}'})

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>/record/stop', methods=['POST'])
def stop_test_recording(project_id, suite_id, test_id): # Remove recorder.stop_recording() and project_manager.save() and use project_manager.stop_recording(project_id, suite_id, test_id)
 test = find_test_by_id(suite.tests, test_id)
 if test is None:
 return jsonify({'error': 'Test not found'}), 404
 steps = recorder.stop_recording()
 project_manager.save()
 return jsonify({'message': f'Recording stopped for test: {test.name}', 'steps_recorded': len(steps)})
@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>/run', methods=['POST'])
def run_test(project_id, suite_id, test_id):
 
 test = project_manager.play_test(project_id, suite_id, test_id)

    player = Player()
 player.play(test)
 project_manager.save() # Assuming playback might update test results

 return jsonify({'message': f'Test {test.name} played successfully'})


if __name__ == "__main__":
    app.run(debug=True)
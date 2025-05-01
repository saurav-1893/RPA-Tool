from flask import Flask, jsonify, request, render_template
from functools import wraps
from .utils.project_manager import ProjectManager

app = Flask(__name__)
project_manager = ProjectManager()

# ================= Helper Decorators =================
def validate_project(f):
    @wraps(f)
    def decorated_function(project_id, *args, **kwargs):
        if not project_manager.get_project(project_id):
            return jsonify({'error': 'Project not found'}), 404
        return f(project_id, *args, **kwargs)
    return decorated_function

def validate_suite(f):
    @wraps(f)
    def decorated_function(project_id, suite_id, *args, **kwargs):
        project = project_manager.get_project(project_id)
        suite = next((s for s in project.test_suites if s.id == suite_id), None)
        if not suite:
            return jsonify({'error': 'Test Suite not found'}), 404
        return f(project_id, suite_id, *args, **kwargs)
    return decorated_function

# ================= Frontend Routes =================
@app.route('/')
def main():
    projects = project_manager.get_all_projects()
    return render_template('index.html', projects=projects)

@app.route('/project/<project_id>')
def project_detail(project_id):
    project = project_manager.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    return render_template('project.html', project=project)

# ================= API Routes =================
@app.route('/api/projects', methods=['GET'])
def get_all_projects():
    projects = project_manager.get_all_projects()
    return jsonify([p.to_dict() for p in projects])

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Project name is required'}), 400
    
    try:
        new_project = project_manager.create_project(data['name'])
        return jsonify(new_project.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/suites', methods=['GET'])
@validate_project
def get_suites(project_id):
    project = project_manager.get_project(project_id)
    return jsonify([s.to_dict() for s in project.test_suites])

@app.route('/api/projects/<project_id>/suites', methods=['POST'])
@validate_project
def create_suite(project_id):
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Suite name is required'}), 400

    try:
        test_suite = project_manager.create_test_suite(project_id, data['name'])
        return jsonify(test_suite.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests', methods=['GET'])
@validate_project
@validate_suite
def get_tests(project_id, suite_id):
    project = project_manager.get_project(project_id)
    suite = next((s for s in project.test_suites if s.id == suite_id), None)
    return jsonify([t.to_dict() for t in suite.tests])

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests', methods=['POST'])
@validate_project
@validate_suite
def create_test(project_id, suite_id):
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Test name is required'}), 400
    
    try:
        test = project_manager.create_test(project_id, suite_id, data['name'])
        return jsonify(test.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>/record/start', methods=['POST'])
@validate_project
@validate_suite
def start_test_recording(project_id, suite_id, test_id):
    test = project_manager.get_test(project_id, suite_id, test_id)
    if not test:
        return jsonify({'error': 'Test not found'}), 404
    if test.is_recording:
        return jsonify({'error': 'Recording already in progress'}), 409
    
    project_manager.start_recording(test_id)
    return jsonify({'message': 'Recording started', 'test_id': test_id})

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>/record/stop', methods=['POST'])
@validate_project
@validate_suite
def stop_test_recording(project_id, suite_id, test_id):
    test = project_manager.get_test(project_id, suite_id, test_id)
    if not test:
        return jsonify({'error': 'Test not found'}), 404
    if not test.is_recording:
        return jsonify({'error': 'No recording in progress for this test'}), 409
    
    result = project_manager.stop_recording(test_id)
    return jsonify({
        'message': 'Recording stopped',
        'steps_recorded': len(result['steps']),
        'test_id': test_id
    })

@app.route('/api/projects/<project_id>/run', methods=['POST'])
@validate_project
def run_all_tests_in_project(project_id):
    try:
        results = project_manager.run_all_tests(project_id)
        return jsonify({
            'message': 'Tests executed',
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ================= Error Handlers =================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__":
    app.run(debug=True)

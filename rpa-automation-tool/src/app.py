import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from flask import Flask, jsonify, request, render_template
import logging
from functools import wraps
import traceback
from src.utils.project_manager import ProjectManager

app = Flask(__name__)
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app.logger.setLevel(logging.INFO)

# Initialize project manager
project_manager = ProjectManager()

# ================= Helper Decorators =================
def handle_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            app.logger.error(f"Error in {f.__name__}: {str(e)}\n{traceback.format_exc()}")
            return jsonify({'error': str(e)}), 500
    return decorated_function

def validate_project(f):
    @wraps(f)
    def decorated_function(project_id, *args, **kwargs):
        project = project_manager.get_project(project_id)
        if not project:
            app.logger.warning(f"Project not found: {project_id}")
            return jsonify({'error': 'Project not found'}), 404
        return f(project_id, *args, **kwargs)
    return decorated_function

def validate_suite(f):
    @wraps(f)
    def decorated_function(project_id, suite_id, *args, **kwargs):
        project = project_manager.get_project(project_id)
        if not project:
            app.logger.warning(f"Project not found: {project_id}")
            return jsonify({'error': 'Project not found'}), 404
        suite = next((s for s in project.test_suites if s.id == suite_id), None)
        if not suite:
            app.logger.warning(f"Test Suite not found: {suite_id} in project {project_id}")
            return jsonify({'error': 'Test Suite not found'}), 404
        return f(project_id, suite_id, *args, **kwargs)
    return decorated_function

def validate_test(f):
    @wraps(f)
    def decorated_function(project_id, suite_id, test_id, *args, **kwargs):
        project = project_manager.get_project(project_id)
        if not project:
            app.logger.warning(f"Project not found: {project_id}")
            return jsonify({'error': 'Project not found'}), 404
        suite = next((s for s in project.test_suites if s.id == suite_id), None)
        if not suite:
            app.logger.warning(f"Test Suite not found: {suite_id} in project {project_id}")
            return jsonify({'error': 'Test Suite not found'}), 404
        test = next((t for t in suite.tests if t.id == test_id), None)
        if not test:
            app.logger.warning(f"Test not found: {test_id} in suite {suite_id}, project {project_id}")
            return jsonify({'error': 'Test not found'}), 404
        return f(project_id, suite_id, test_id, *args, **kwargs)
    return decorated_function

def require_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 415
        return f(*args, **kwargs)
    return decorated_function

# ================= Frontend Routes =================
@app.route('/')
@handle_exceptions
def main():
    """Render the main page with all projects."""
    projects = project_manager.get_all_projects()
    return render_template('index.html', projects=projects)

@app.route('/project/<project_id>')
@handle_exceptions
def project_detail(project_id):
    """Render a specific project page."""
    project = project_manager.get_project(project_id)
    if not project:
        app.logger.warning(f"Project not found for detail page: {project_id}")
        return render_template('error.html', error="Project not found"), 404
    return render_template('project.html', project=project)

@app.route('/project/<project_id>/suite/<suite_id>')
@handle_exceptions
def suite_detail(project_id, suite_id):
    """Render a specific test suite page."""
    project = project_manager.get_project(project_id)
    if not project:
        app.logger.warning(f"Project not found for suite detail page: {project_id}")
        return render_template('error.html', error="Project not found"), 404
    suite = next((s for s in project.test_suites if s.id == suite_id), None)
    if not suite:
        app.logger.warning(f"Test Suite not found: {suite_id} in project {project_id}")
        return render_template('error.html', error="Test Suite not found"), 404
    return render_template('test_suite.html', project=project, suite=suite)

# ================= API Routes =================
@app.route('/api/projects', methods=['GET'])
@handle_exceptions
def get_all_projects():
    """Get all projects."""
    projects = project_manager.get_all_projects()
    return jsonify([p.to_dict() for p in projects])

@app.route('/api/projects/<project_id>', methods=['GET'])
@validate_project
@handle_exceptions
def get_project(project_id):
    """Get a specific project by ID."""
    project = project_manager.get_project(project_id)
    return jsonify(project.to_dict())

@app.route('/api/projects', methods=['POST'])
@require_json
@handle_exceptions
def create_project():
    """Create a new project."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Project name is required'}), 400
    new_project = project_manager.create_project(data['name'])
    app.logger.info(f"Created new project: {new_project.id}")
    return jsonify(new_project.to_dict()), 201

@app.route('/api/projects/<project_id>', methods=['PUT'])
@validate_project
@require_json
@handle_exceptions
def update_project(project_id):
    """Update an existing project."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Project name is required'}), 400
    updated_project = project_manager.update_project(project_id, data['name'])
    app.logger.info(f"Updated project: {project_id}")
    return jsonify(updated_project.to_dict())

@app.route('/api/projects/<project_id>', methods=['DELETE'])
@validate_project
@handle_exceptions
def delete_project(project_id):
    """Delete a project."""
    project_manager.delete_project(project_id)
    app.logger.info(f"Deleted project: {project_id}")
    return jsonify({'message': 'Project deleted successfully'})

@app.route('/api/projects/<project_id>/suites', methods=['GET'])
@validate_project
@handle_exceptions
def get_suites(project_id):
    """Get all test suites for a project."""
    project = project_manager.get_project(project_id)
    return jsonify([s.to_dict() for s in project.test_suites])

@app.route('/api/projects/<project_id>/suites/<suite_id>', methods=['GET'])
@validate_project
@validate_suite
@handle_exceptions
def get_suite(project_id, suite_id):
    """Get a specific test suite."""
    project = project_manager.get_project(project_id)
    suite = next((s for s in project.test_suites if s.id == suite_id), None)
    return jsonify(suite.to_dict())

@app.route('/api/projects/<project_id>/suites', methods=['POST'])
@validate_project
@require_json
@handle_exceptions
def create_suite(project_id):
    """Create a new test suite in a project."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Suite name is required'}), 400
    test_suite = project_manager.create_test_suite(project_id, data['name'])
    app.logger.info(f"Created test suite {test_suite.id} in project {project_id}")
    return jsonify(test_suite.to_dict()), 201

@app.route('/api/projects/<project_id>/suites/<suite_id>', methods=['PUT'])
@validate_project
@validate_suite
@require_json
@handle_exceptions
def update_suite(project_id, suite_id):
    """Update a test suite."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Suite name is required'}), 400
    updated_suite = project_manager.update_test_suite(project_id, suite_id, data['name'])
    app.logger.info(f"Updated test suite {suite_id} in project {project_id}")
    return jsonify(updated_suite.to_dict())

@app.route('/api/projects/<project_id>/suites/<suite_id>', methods=['DELETE'])
@validate_project
@validate_suite
@handle_exceptions
def delete_suite(project_id, suite_id):
    """Delete a test suite."""
    project_manager.delete_test_suite(project_id, suite_id)
    app.logger.info(f"Deleted test suite {suite_id} from project {project_id}")
    return jsonify({'message': 'Test suite deleted successfully'})

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests', methods=['GET'])
@validate_project
@validate_suite
@handle_exceptions
def get_tests(project_id, suite_id):
    """Get all tests in a test suite."""
    project = project_manager.get_project(project_id)
    suite = next((s for s in project.test_suites if s.id == suite_id), None)
    return jsonify([t.to_dict() for t in suite.tests])

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>', methods=['GET'])
@validate_project
@validate_suite
@validate_test
@handle_exceptions
def get_test(project_id, suite_id, test_id):
    """Get a specific test from a suite."""
    project = project_manager.get_project(project_id)
    suite = next((s for s in project.test_suites if s.id == suite_id), None)
    test = next((t for t in suite.tests if t.id == test_id), None)
    return jsonify(test.to_dict())

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests', methods=['POST'])
@validate_project
@validate_suite
@require_json
@handle_exceptions
def create_test(project_id, suite_id):
    """Create a new test in a test suite."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Test name is required'}), 400
    test = project_manager.create_test(project_id, suite_id, data['name'])
    app.logger.info(f"Created test {test.id} in suite {suite_id}")
    return jsonify(test.to_dict()), 201

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>', methods=['PUT'])
@validate_project
@validate_suite
@validate_test
@require_json
@handle_exceptions
def update_test(project_id, suite_id, test_id):
    """Update a test."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Test name is required'}), 400
    updated_test = project_manager.update_test(project_id, suite_id, test_id, data['name'])
    app.logger.info(f"Updated test {test_id}")
    return jsonify(updated_test.to_dict())

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>', methods=['DELETE'])
@validate_project
@validate_suite
@validate_test
@handle_exceptions
def delete_test(project_id, suite_id, test_id):
    """Delete a test."""
    project_manager.delete_test(project_id, suite_id, test_id)
    app.logger.info(f"Deleted test {test_id}")
    return jsonify({'message': 'Test deleted successfully'})

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>/record/start', methods=['POST'])
@validate_project
@validate_suite
@validate_test
@handle_exceptions
def start_test_recording(project_id, suite_id, test_id):
    """Start recording a test."""
    result = project_manager.start_recording(project_id, suite_id, test_id)
    if result:
        app.logger.info(f"Started recording for test {test_id}")
        return jsonify({'message': 'Recording started', 'test_id': test_id})
    else:
        app.logger.warning(f"Recording already in progress for test {test_id}")
        return jsonify({'error': 'Recording already in progress or could not start recording'}), 409

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>/record/stop', methods=['POST'])
@validate_project
@validate_suite
@validate_test
@handle_exceptions
def stop_test_recording(project_id, suite_id, test_id):
    """Stop recording a test."""
    result = project_manager.stop_recording(project_id, suite_id, test_id)
    if result:
        steps_recorded = len(result.steps) if hasattr(result, 'steps') else 0
        app.logger.info(f"Stopped recording for test {test_id}, {steps_recorded} steps recorded")
        return jsonify({
            'message': 'Recording stopped',
            'steps_recorded': steps_recorded,
            'test_id': test_id
        })
    else:
        app.logger.warning(f"No recording in progress for test {test_id}")
        return jsonify({'error': 'No recording in progress for this test'}), 409

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>/play', methods=['POST'])
@validate_project
@validate_suite
@validate_test
@handle_exceptions
def play_test(project_id, suite_id, test_id):
    """Play a test."""
    result = project_manager.play_test(project_id, suite_id, test_id)
    app.logger.info(f"Played test {test_id}")
    return jsonify({
        'message': 'Test played',
        'result': 'success' if result else 'failure',
        'test_id': test_id
    })

@app.route('/api/projects/<project_id>/run', methods=['POST'])
@validate_project
@handle_exceptions
def run_all_tests_in_project(project_id):
    """Run all tests in a project."""
    results = project_manager.run_all_tests(project_id)
    app.logger.info(f"Ran all tests for project {project_id}")
    return jsonify({
        'message': 'Tests executed',
        'results': results
    })

@app.route('/api/projects/<project_id>/suites/<suite_id>/run', methods=['POST'])
@validate_project
@validate_suite
@handle_exceptions
def run_suite_tests(project_id, suite_id):
    """Run all tests in a specific test suite."""
    results = project_manager.run_suite_tests(project_id, suite_id)
    app.logger.info(f"Ran all tests for suite {suite_id}")
    return jsonify({
        'message': 'Suite tests executed',
        'results': results
    })

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>/run', methods=['POST'])
@validate_project
@validate_suite
@validate_test
@handle_exceptions
def run_single_test(project_id, suite_id, test_id):
    """Run a single test."""
    result = project_manager.run_test(project_id, suite_id, test_id)
    app.logger.info(f"Ran test {test_id}")
    return jsonify({
        'message': 'Test executed',
        'result': result
    })

# ================= Status Routes =================
@app.route('/api/status', methods=['GET'])
@handle_exceptions
def get_status():
    """Get system status."""
    status = {
        'status': 'operational',
        'version': '1.0.0',
        'project_count': len(project_manager.get_all_projects())
    }
    return jsonify(status)

# ================= Error Handlers =================
@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 Internal Server Error."""
    app.logger.error(f"500 error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 Method Not Allowed."""
    app.logger.warning(f"405 error: {request.method} {request.path}")
    return jsonify({'error': f'Method {request.method} not allowed'}), 405

@app.errorhandler(415)
def unsupported_media_type(error):
    """Handle 415 Unsupported Media Type."""
    app.logger.warning(f"415 error: {request.content_type}")
    return jsonify({'error': 'Unsupported media type'}), 415

if __name__ == "__main__":
    app.run(debug=True)
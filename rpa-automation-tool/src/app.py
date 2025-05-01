import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from flask import Flask, jsonify, request, render_template, abort
import logging
from functools import wraps
import traceback
from src.utils.project_manager import ProjectManager

app = Flask(__name__)
# Configure logging
app.logger.setLevel(logging.INFO)

# Initialize project manager
project_manager = ProjectManager()

# ================= Helper Decorators =================
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
        test = project_manager.get_test(project_id, suite_id, test_id)
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
def main():
    """Render the main page with all projects."""
    try:
        projects = project_manager.get_all_projects()
        return render_template('index.html', projects=projects)
    except Exception as e:
        app.logger.error(f"Error rendering main page: {str(e)}")
        return render_template('error.html', error=str(e)), 500

@app.route('/project/<project_id>')
def project_detail(project_id):
    """Render a specific project page."""
    project = project_manager.get_project(project_id)
    if not project:
        app.logger.warning(f"Project not found for detail page: {project_id}")
        return render_template('error.html', error="Project not found"), 404
    return render_template('project.html', project=project)

# ================= API Routes =================
@app.route('/api/projects', methods=['GET'])
def get_all_projects():
    """Get all projects."""
    try:
        projects = project_manager.get_all_projects()
        return jsonify([p.to_dict() for p in projects])
    except Exception as e:
        app.logger.error(f"Error getting all projects: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['GET'])
@validate_project
def get_project(project_id):
    """Get a specific project by ID."""
    project = project_manager.get_project(project_id)
    return jsonify(project.to_dict())

@app.route('/api/projects', methods=['POST'])
@require_json
def create_project():
    """Create a new project."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Project name is required'}), 400
    
    try:
        new_project = project_manager.create_project(data['name'])
        app.logger.info(f"Created new project: {new_project.id}")
        return jsonify(new_project.to_dict()), 201
    except Exception as e:
        app.logger.error(f"Error creating project: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['PUT'])
@validate_project
@require_json
def update_project(project_id):
    """Update an existing project."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Project name is required'}), 400
    
    try:
        updated_project = project_manager.update_project(project_id, data['name'])
        app.logger.info(f"Updated project: {project_id}")
        return jsonify(updated_project.to_dict())
    except Exception as e:
        app.logger.error(f"Error updating project {project_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['DELETE'])
@validate_project
def delete_project(project_id):
    """Delete a project."""
    try:
        project_manager.delete_project(project_id)
        app.logger.info(f"Deleted project: {project_id}")
        return jsonify({'message': 'Project deleted successfully'})
    except Exception as e:
        app.logger.error(f"Error deleting project {project_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/suites', methods=['GET'])
@validate_project
def get_suites(project_id):
    """Get all test suites for a project."""
    project = project_manager.get_project(project_id)
    return jsonify([s.to_dict() for s in project.test_suites])

@app.route('/api/projects/<project_id>/suites/<suite_id>', methods=['GET'])
@validate_project
@validate_suite
def get_suite(project_id, suite_id):
    """Get a specific test suite."""
    project = project_manager.get_project(project_id)
    suite = next((s for s in project.test_suites if s.id == suite_id), None)
    return jsonify(suite.to_dict())

@app.route('/api/projects/<project_id>/suites', methods=['POST'])
@validate_project
@require_json
def create_suite(project_id):
    """Create a new test suite in a project."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Suite name is required'}), 400

    try:
        test_suite = project_manager.create_test_suite(project_id, data['name'])
        app.logger.info(f"Created test suite {test_suite.id} in project {project_id}")
        return jsonify(test_suite.to_dict()), 201
    except Exception as e:
        app.logger.error(f"Error creating test suite in project {project_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/suites/<suite_id>', methods=['PUT'])
@validate_project
@validate_suite
@require_json
def update_suite(project_id, suite_id):
    """Update a test suite."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Suite name is required'}), 400
    
    try:
        updated_suite = project_manager.update_test_suite(project_id, suite_id, data['name'])
        app.logger.info(f"Updated test suite {suite_id} in project {project_id}")
        return jsonify(updated_suite.to_dict())
    except Exception as e:
        app.logger.error(f"Error updating test suite {suite_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/suites/<suite_id>', methods=['DELETE'])
@validate_project
@validate_suite
def delete_suite(project_id, suite_id):
    """Delete a test suite."""
    try:
        project_manager.delete_test_suite(project_id, suite_id)
        app.logger.info(f"Deleted test suite {suite_id} from project {project_id}")
        return jsonify({'message': 'Test suite deleted successfully'})
    except Exception as e:
        app.logger.error(f"Error deleting test suite {suite_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests', methods=['GET'])
@validate_project
@validate_suite
def get_tests(project_id, suite_id):
    """Get all tests in a test suite."""
    project = project_manager.get_project(project_id)
    suite = next((s for s in project.test_suites if s.id == suite_id), None)
    return jsonify([t.to_dict() for t in suite.tests])

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>', methods=['GET'])
@validate_project
@validate_suite
@validate_test
def get_test(project_id, suite_id, test_id):
    """Get a specific test."""
    test = project_manager.get_test(project_id, suite_id, test_id)
    return jsonify(test.to_dict())

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests', methods=['POST'])
@validate_project
@validate_suite
@require_json
def create_test(project_id, suite_id):
    """Create a new test in a test suite."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Test name is required'}), 400
    
    try:
        test = project_manager.create_test(project_id, suite_id, data['name'])
        app.logger.info(f"Created test {test.id} in suite {suite_id}")
        return jsonify(test.to_dict()), 201
    except Exception as e:
        app.logger.error(f"Error creating test in suite {suite_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>', methods=['PUT'])
@validate_project
@validate_suite
@validate_test
@require_json
def update_test(project_id, suite_id, test_id):
    """Update a test."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Test name is required'}), 400
    
    try:
        updated_test = project_manager.update_test(project_id, suite_id, test_id, data['name'])
        app.logger.info(f"Updated test {test_id}")
        return jsonify(updated_test.to_dict())
    except Exception as e:
        app.logger.error(f"Error updating test {test_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>', methods=['DELETE'])
@validate_project
@validate_suite
@validate_test
def delete_test(project_id, suite_id, test_id):
    """Delete a test."""
    try:
        project_manager.delete_test(project_id, suite_id, test_id)
        app.logger.info(f"Deleted test {test_id}")
        return jsonify({'message': 'Test deleted successfully'})
    except Exception as e:
        app.logger.error(f"Error deleting test {test_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>/record/start', methods=['POST'])
@validate_project
@validate_suite
@validate_test
def start_test_recording(project_id, suite_id, test_id):
    """Start recording a test."""
    test = project_manager.get_test(project_id, suite_id, test_id)
    if test.is_recording:
        app.logger.warning(f"Recording already in progress for test {test_id}")
        return jsonify({'error': 'Recording already in progress'}), 409
    
    try:
        project_manager.start_recording(test_id)
        app.logger.info(f"Started recording for test {test_id}")
        return jsonify({'message': 'Recording started', 'test_id': test_id})
    except Exception as e:
        app.logger.error(f"Error starting recording for test {test_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>/record/stop', methods=['POST'])
@validate_project
@validate_suite
@validate_test
def stop_test_recording(project_id, suite_id, test_id):
    """Stop recording a test."""
    test = project_manager.get_test(project_id, suite_id, test_id)
    if not test.is_recording:
        app.logger.warning(f"No recording in progress for test {test_id}")
        return jsonify({'error': 'No recording in progress for this test'}), 409
    
    try:
        result = project_manager.stop_recording(test_id)
        app.logger.info(f"Stopped recording for test {test_id}, {len(result['steps'])} steps recorded")
        return jsonify({
            'message': 'Recording stopped',
            'steps_recorded': len(result['steps']),
            'test_id': test_id
        })
    except Exception as e:
        app.logger.error(f"Error stopping recording for test {test_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/run', methods=['POST'])
@validate_project
def run_all_tests_in_project(project_id):
    """Run all tests in a project."""
    try:
        results = project_manager.run_all_tests(project_id)
        app.logger.info(f"Ran all tests for project {project_id}")
        return jsonify({
            'message': 'Tests executed',
            'results': results
        })
    except Exception as e:
        app.logger.error(f"Error running tests for project {project_id}: {str(e)}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/projects/<project_id>/suites/<suite_id>/run', methods=['POST'])
@validate_project
@validate_suite
def run_suite_tests(project_id, suite_id):
    """Run all tests in a specific test suite."""
    try:
        results = project_manager.run_suite_tests(project_id, suite_id)
        app.logger.info(f"Ran all tests for suite {suite_id}")
        return jsonify({
            'message': 'Suite tests executed',
            'results': results
        })
    except Exception as e:
        app.logger.error(f"Error running tests for suite {suite_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>/run', methods=['POST'])
@validate_project
@validate_suite
@validate_test
def run_single_test(project_id, suite_id, test_id):
    """Run a single test."""
    try:
        result = project_manager.run_test(project_id, suite_id, test_id)
        app.logger.info(f"Ran test {test_id}")
        return jsonify({
            'message': 'Test executed',
            'result': result
        })
    except Exception as e:
        app.logger.error(f"Error running test {test_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ================= Status Routes =================
@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status."""
    try:
        status = {
            'status': 'operational',
            'version': '1.0.0',
            'project_count': len(project_manager.get_all_projects())
        }
        return jsonify(status)
    except Exception as e:
        app.logger.error(f"Error getting system status: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

# ================= Error Handlers =================
@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    app.logger.warning(f"404 error: {request.path}")
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

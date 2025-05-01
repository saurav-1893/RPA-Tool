import sys
    from pathlib import Path

    # Add project root to Python path
    PROJECT_ROOT = Path(__file__).parent.parent
    sys.path.append(str(PROJECT_ROOT))
from flask import Flask, jsonify, request, render_template, logging
from functools import wraps
import traceback
import sys
import os

# Fix import issues when running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

@app.route('/api/projects/<project_id>/suites', methods=['GET'])
@validate_project
def get_suites(project_id):
    """Get all test suites for a project."""
    project = project_manager.get_project(project_id)
    return jsonify([s.to_dict() for s in project.test_suites])

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests', methods=['GET'])
@validate_project
@validate_suite
def get_tests(project_id, suite_id):
    """Get all tests in a test suite."""
    project = project_manager.get_project(project_id)
    suite = next((s for s in project.test_suites if s.id == suite_id), None)
    return jsonify([t.to_dict() for t in suite.tests])

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

@app.route('/api/projects/<project_id>/suites/<suite_id>/tests/<test_id>/record/start', methods=['POST'])
@validate_project
@validate_suite
def start_test_recording(project_id, suite_id, test_id):
    """Start recording a test."""
    test = project_manager.get_test(project_id, suite_id, test_id)
    if not test:
        return jsonify({'error': 'Test not found'}), 404
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
def stop_test_recording(project_id, suite_id, test_id):
    """Stop recording a test."""
    test = project_manager.get_test(project_id, suite_id, test_id)
    if not test:
        return jsonify({'error': 'Test not found'}), 404
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
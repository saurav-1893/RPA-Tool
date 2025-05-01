from flask import Flask, jsonify
from models.project import Project
from models.test import Test
from models.step import Step
from utils.data import load_projects, save_projects
from core.runner import Runner

app = Flask(__name__)

projects = load_projects()

@app.route("/")
def main():
    return "RPA Automation Tool"

@app.route('/api/projects', methods=['GET'])
def get_all_projects():
    return jsonify([p.__dict__ for p in projects])

@app.route('/api/run', methods=['POST'])
def run_all_tests():
    runner = Runner()
    results = runner.run(projects)
    save_projects(projects)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
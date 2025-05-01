import json
import os
from ..models.project import Project
from ..models.test_suite import TestSuite
from ..models.test import Test
from ..models.step import Step
from json import JSONEncoder

def load_projects(filepath="projects.json"):
    """Loads projects from a JSON file or returns an empty list if the file doesn't exist."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        data = json.load(f)
        return [Project.from_dict(project_data) for project_data in data]

def save_projects(projects, filepath="projects.json"):
    """Saves projects to a JSON file."""
    project_data = [project.to_dict() for project in projects]
    with open(filepath, "w") as f:
        json.dump(project_data, f, indent=4, cls=CustomEncoder)

class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Project):
            return obj.to_dict()
        if isinstance(obj, TestSuite):
            return obj.to_dict()
        if isinstance(obj, Test):
            return obj.to_dict()
        if isinstance(obj, Step):
            return obj.to_dict()
        return JSONEncoder.default(self, obj)
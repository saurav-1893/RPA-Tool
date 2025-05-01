import json
import os

def load_projects(filepath="projects.json"):
    """Loads projects from a JSON file or returns an empty list if the file doesn't exist."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError:
        return []

def save_projects(projects, filepath="projects.json"):
    """Saves projects to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(projects, f, indent=4)
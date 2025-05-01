# src/api/api_client.py
import requests
import json


def make_api_request(url, method="GET", headers=None, data=None, json=None):
    """
    Makes an API request to the given URL with the specified method.
    """
    # Ensure headers is a dictionary, even if None is passed
    headers = headers if headers is not None else {}

    response = requests.request(method, url, headers=headers, data=data, json=json)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    return response


def get_projects(base_url):
    """
    Gets all projects from the API.
    """
    url = f"{base_url}/api/projects"
    response = make_api_request(url)
    return response.json()


def create_project(base_url, project_name):
    """
    Creates a new project via the API.
    """
    url = f"{base_url}/api/projects"
    data = {"name": project_name}
    response = make_api_request(url, method="POST", json=data)
    return response.json()
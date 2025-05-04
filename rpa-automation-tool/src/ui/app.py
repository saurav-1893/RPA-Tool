import tkinter as tk
from tkinter import ttk
import requests

from src.utils.project_manager import ProjectManager
project_manager = ProjectManager()

class RPAApp:
    API_BASE_URL = "http://127.0.0.1:5000/api"  # Assuming Flask is running on default port

    def __init__(self, root):
        self.root = root
        root.title("RPA Automation Tool")

        self.create_menu()
        self.create_recording_section()
        self.create_playback_section()
        self.create_status_bar()

        self.is_recording = False
        self.current_project = None
        self.current_suite = None
        self.current_test = None

        self.projects = []
        self.test_suites = []
        self.recorded_actions = []

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Check API Status", command=self.check_api_status)


        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def create_recording_section(self):
        recording_frame = ttk.LabelFrame(self.root, text="Recording")
        recording_frame.pack(fill=tk.BOTH, padx=10, pady=10)

        self.start_button = tk.Button(recording_frame, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=(0, 5))

        self.stop_button = tk.Button(recording_frame, text="Stop Recording", command=self.stop_recording, state=tk.NORMAL)
        self.stop_button.pack(pady=(0, 5))

        self.add_action_button = tk.Button(recording_frame, text="Add new Action", command=self.add_action, state=tk.NORMAL)
        self.add_action_button.pack(pady=(0, 5))

        self.actions_listbox = tk.Listbox(recording_frame, height=10, width=50)
        self.actions_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

    def create_playback_section(self):
        playback_frame = ttk.LabelFrame(self.root, text="Execution")
        playback_frame.pack(fill=tk.BOTH, padx=10, pady=10)

        self.run_button = tk.Button(playback_frame, text="Run last Recording", command=self.run_recording, state=tk.DISABLED)
        self.run_button.pack(pady=(0, 5))

        self.pause_button = tk.Button(playback_frame, text="Pause", command=self.pause_recording, state=tk.DISABLED)
        self.pause_button.pack(pady=(0, 5))

        self.stop_playback_button = tk.Button(playback_frame, text="Stop", command=self.stop_playback, state=tk.NORMAL)
        self.stop_playback_button.pack(pady=(0, 5))

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def send_api_request(self, method, endpoint, data=None):
        try:
            response = requests.request(method, f"{self.API_BASE_URL}/{endpoint}", json=data)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            self.status_var.set(f"API Error: {e}")
    def start_recording(self):
        self.status_var.set("Recording...")
        self.is_recording = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.add_action_button.config(state=tk.NORMAL)
        self.recorded_actions.clear()
        self.actions_listbox.delete(0, tk.END)
        self.run_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_playback_button.config(state=tk.DISABLED)
        print("Starting Recording...")
        # TODO: Implement recording logic

    def stop_recording(self):
        self.status_var.set("Ready")
        self.is_recording = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.add_action_button.config(state=tk.DISABLED)
        self.run_button.config(state=tk.NORMAL)
        print("Stopped Recording.")
        # TODO: Implement stop recording logic

    def add_action(self):
        if self.is_recording:
            action = f"Action {len(self.recorded_actions) + 1}"
            self.recorded_actions.append(action)
            self.actions_listbox.insert(tk.END, action)
            print("Add action")
        # TODO: Implement add new action logic

    def run_recording(self):
        self.status_var.set("Running...")
        self.run_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_playback_button.config(state=tk.NORMAL)
        print("Running the last recording...")
        # TODO: Implement playback logic

    def pause_recording(self):
        self.status_var.set("Paused")
        self.pause_button.config(state=tk.DISABLED)
        self.stop_playback_button.config(state=tk.NORMAL)
        self.run_button.config(state=tk.NORMAL)
        print("Pause recording")
        # TODO: Implement pause recording logic

    def stop_playback(self):
        self.status_var.set("Ready")
        self.pause_button.config(state=tk.DISABLED)
        self.stop_playback_button.config(state=tk.DISABLED)
        self.run_button.config(state=tk.NORMAL)
        print("Stop recording")
        # TODO: Implement stop recording logic

    def create_project(self, name, description):
        """Creates a new project via API."""
        data = {"name": name, "description": description}
        response = self.send_api_request("POST", "projects", data)
        if response:
            self.projects.append(response)
            self.status_var.set(f"Project created: {response.get('name')}")
            # TODO: Update UI to show new project

    def get_projects(self):
        """Fetches all projects from the API."""
        response = self.send_api_request("GET", "projects")
        if response:
            self.projects = response
            self.status_var.set(f"Loaded {len(self.projects)} projects.")
            # TODO: Update UI to display projects

    def update_project(self, project_id, name, description):
        """Updates an existing project via API."""
        data = {"name": name, "description": description}
        response = self.send_api_request("PUT", f"projects/{project_id}", data)
        if response:
            # Find and update the project in the local list
            for i, project in enumerate(self.projects):
                if project.get("id") == project_id:
                    self.projects[i] = response
                    break
            self.status_var.set(f"Project updated: {response.get('name')}")
            # TODO: Update UI to reflect changes

    def delete_project(self, project_id):
        """Deletes a project via API."""
        response = self.send_api_request("DELETE", f"projects/{project_id}")
        if response:
            self.projects = [p for p in self.projects if p.get("id") != project_id]
            self.status_var.set(f"Project deleted: {project_id}")
            # TODO: Update UI to remove project

    def create_suite(self, project_id, name, description):
        """Creates a new test suite via API."""
        data = {"name": name, "description": description}
        response = self.send_api_request("POST", f"projects/{project_id}/suites", data)
        if response:
            self.status_var.set(f"Suite created: {response.get('name')}")
            # TODO: Update UI for the specific project to show new suite

    def get_suites(self, project_id):
        """Fetches all test suites for a project from the API."""
        response = self.send_api_request("GET", f"projects/{project_id}/suites")
        if response:
            self.test_suites = response
            self.status_var.set(f"Loaded {len(self.test_suites)} suites for project {project_id}.")
            # TODO: Update UI to display suites

    def update_suite(self, project_id, suite_id, name, description):
        """Updates an existing test suite via API."""
        data = {"name": name, "description": description}
        response = self.send_api_request("PUT", f"projects/{project_id}/suites/{suite_id}", data)
        if response:
            self.status_var.set(f"Suite updated: {response.get('name')}")
            # TODO: Update UI to reflect changes for the specific suite

    def delete_suite(self, project_id, suite_id):
        """Deletes a test suite via API."""
        response = self.send_api_request("DELETE", f"projects/{project_id}/suites/{suite_id}")
        if response:
            self.status_var.set(f"Suite deleted: {suite_id}")
            # TODO: Update UI to remove suite

    def create_test(self, project_id, suite_id, name):
        """Creates a new test via API."""
        data = {"name": name}
        response = self.send_api_request("POST", f"projects/{project_id}/suites/{suite_id}/tests", data)
        if response:
            self.status_var.set(f"Test created: {response.get('name')}")
            # TODO: Update UI for the specific suite to show new test

    def get_tests(self, project_id, suite_id):
        """Fetches all tests for a test suite from the API."""
        response = self.send_api_request("GET", f"projects/{project_id}/suites/{suite_id}/tests")
        if response:
            self.status_var.set(f"Loaded {len(response)} tests for suite {suite_id}.")
            # TODO: Update UI to display tests

    def update_test(self, project_id, suite_id, test_id, name):
        """Updates an existing test via API."""
        data = {"name": name}
        response = self.send_api_request("PUT", f"projects/{project_id}/suites/{suite_id}/tests/{test_id}", data)
        if response:
            self.status_var.set(f"Test updated: {response.get('name')}")
            # TODO: Update UI to reflect changes for the specific test

    def delete_test(self, project_id, suite_id, test_id):
        """Deletes a test via API."""
        response = self.send_api_request("DELETE", f"projects/{project_id}/suites/{suite_id}/tests/{test_id}")
        if response:
            self.status_var.set(f"Test deleted: {test_id}")
            # TODO: Update UI to remove test

    
    def show_about(self):
        print("Show about")
        # TODO: show about logic

    def check_api_status(self):
        """Checks the status of the API."""
        response = self.send_api_request("GET", "status")
        if response:
            self.status_var.set(f"API Status: {response.get('status', 'Unknown')}")
        else:
            self.status_var.set("API Status: Not reachable")

    def run_all_tests(self, project_id):
        """Runs all tests in a project via API."""
        response = self.send_api_request("POST", f"projects/{project_id}/run")
        if response:
            self.status_var.set(f"Running all tests for project {project_id}...")

    def run_suite(self, project_id, suite_id):
        """Runs all tests in a test suite via API."""
        response = self.send_api_request("POST", f"projects/{project_id}/suites/{suite_id}/run")
        if response:
            self.status_var.set(f"Running tests for suite {suite_id} in project {project_id}...")


if __name__ == "__main__":
    root = tk.Tk()
    app = RPAApp(root)
    root.mainloop()
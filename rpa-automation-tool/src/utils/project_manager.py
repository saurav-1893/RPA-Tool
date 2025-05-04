from src.models.project import Project # Fixed import
from src.models.test import Test # Fixed import
from src.models.test_suite import TestSuite
from .data import load_projects, save_projects
# from src.core.recorder import Recorder # Temporarily commented out
from src.core.player import Player
import logging
from src.core.runner import Runner
class ProjectManager:
    def __init__(self):
        self.projects = load_projects()

    def create_project(self, project_name):
        logging.info(f"Creating project with name: {project_name}")
        project = Project(name=project_name)
        self.projects.append(project)
        logging.info(f"Project added to self.projects. Project ID: {project.id}")
        logging.info(f"Project created with ID: {project.id}")
        self.save()
        return project

    def get_all_projects(self):
        return self.projects

    def create_test_suite(self, project_id, suite_name):
        project = self.get_project(project_id)
        if project:
            test_suite = TestSuite(name=suite_name)
            project.test_suites.append(test_suite)
            self.save()
            return test_suite
        return None

    def get_all_test_suites(self, project_id):
        project = self.get_project(project_id)
        if project:
            return project.test_suites
        return []

    def create_test(self, project_id, suite_id, test_name):
        project = self.get_project(project_id)
        if project:
            test_suite = next(
                (ts for ts in project.test_suites if ts.id == suite_id), None
            )
            if test_suite:
                test = Test(name=test_name)
                test_suite.tests.append(test)
                self.save()
                return test
        return None

    def get_all_tests(self, project_id, suite_id):
        project = self.get_project(project_id)
        if project:
            test_suite = next(
                (ts for ts in project.test_suites if ts.id == suite_id), None
            )
            if test_suite:
                return test_suite.tests
        return []

    def get_project(self, project_id):
        return next((p for p in self.projects if p.id == project_id), None)

    def save(self):
        save_projects(self.projects)

    def get_test_from_suite(self, project_id, suite_id, test_id):
        project = self.get_project(project_id)
        if project:
            test_suite = next((ts for ts in project.test_suites if ts.id == suite_id), None)
            if test_suite:
                test = next((t for t in test_suite.tests if t.id == test_id), None)
                return test
        return None

    def get_test_steps(self, project_id, suite_id, test_id):
        """Gets all steps for a test."""
        test = self.get_test_from_suite(project_id, suite_id, test_id)
        return test.steps if test else []

    def add_step(self, project_id, suite_id, test_id, step_data):
        """Adds a new step to a test."""
        test = self.get_test_from_suite(project_id, suite_id, test_id)
        if test:
            test.steps.append(step_data)
            self.save()
            return step_data
        return None

    def update_step(self, project_id, suite_id, test_id, step_index, step_data):
        """Updates an existing step."""
        test = self.get_test_from_suite(project_id, suite_id, test_id)
        if test and 0 <= step_index < len(test.steps):
            test.steps[step_index] = step_data
            self.save()
            return test.steps[step_index]
        return None

    def delete_step(self, project_id, suite_id, test_id, step_index):
        """Deletes a step."""
        test = self.get_test_from_suite(project_id, suite_id, test_id)
        if test and 0 <= step_index < len(test.steps):
            del test.steps[step_index]
            self.save()
            return True
    def record_test(self, project_id, suite_id, test_id):
        test = self.get_test_from_suite(project_id, suite_id, test_id)
        if test:
            # recorder = Recorder() # Temporarily commented out
            # test.record(recorder) # Temporarily commented out
            test.is_recording = True
            test.is_paused = False
            return True
        return False

    def stop_recording(self, project_id, suite_id, test_id):
        test = self.get_test_from_suite(project_id, suite_id, test_id)
        if test and test.is_recording and not test.is_paused:
            # recorder = Recorder() # Temporarily commented out
            # steps, test = recorder.stop(test) # Temporarily commented out
            # test.record(steps) # Temporarily commented out
            test.is_recording = False
            test.is_paused = False
            recorder = Recorder()
            steps, test = recorder.stop(test)
            test.record(steps)
            self.save()
            return test
        return None

    def pause_recording(self, project_id, suite_id, test_id):
        """Pause the current recording."""
        test = self.get_test_from_suite(project_id, suite_id, test_id)
        if test and test.is_recording and not test.is_paused:
            test.is_paused = True
            return True
        return False
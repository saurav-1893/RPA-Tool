from src.models.project import Project # Fixed import
from src.models.test import Test # Fixed import
from src.models.test_suite import TestSuite
from .data import load_projects, save_projects
from core.recorder import Recorder
from src.models.test import Test # Fixed duplicate import
from core.player import Player
from core.runner import Runner
class ProjectManager:
    def __init__(self):
        self.projects = load_projects()

    def create_project(self, project_name):
        project = Project(name=project_name)
        self.projects.append(project)
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

    def record_test(self, test_id):
        test = self.get_test(test_id)
        if test:
            recorder = Recorder()
            test.start_recording(recorder)
            return True
        return False

    def stop_recording(self, test_id):
        test = self.get_test(test_id)
        if test and test.is_recording:
            recorder = Recorder()
            steps, test = recorder.stop(test)
            test.record(steps)
            self.save()
            return test
        return None
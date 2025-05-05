import uuid
from .test_suite import TestSuite

class Project:
    def __init__(self, name, id=None, test_suites=None, history=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.name = name or "Unnamed Project"  # Ensure name is not None
        self.description = ""  # Add description attribute
        self.test_suites = test_suites if test_suites is not None else []
        self.history = history if history is not None else []

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'test_suites': [suite.to_dict() for suite in self.test_suites],
            'history': self.history, # Add a comma here to fix the syntax error
            'description': self.description  # Include description in dict
        }

    @classmethod
    def from_dict(cls, data):
        test_suites = []
        for suite_data in data.get('test_suites', []):
            if hasattr(TestSuite, 'from_dict'):
                test_suites.append(TestSuite.from_dict(suite_data))
            else:
                test_suites.append(TestSuite(suite_data.get('name')))
        return cls(
            id=data.get('id'),
            name=data.get('name', "Unnamed Project"),
            description=data.get('description', ""),  # Load description from dict
            test_suites=test_suites,
            history=data.get('history', [])
        )
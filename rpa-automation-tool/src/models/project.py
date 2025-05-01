import uuid

class Project:
    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.name = name
        self.test_suites = []
        self.history = []

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'test_suites': [suite.to_dict() for suite in self.test_suites]
        }
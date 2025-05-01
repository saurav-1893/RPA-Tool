import uuid
from .test import Test


class TestSuite:
    def __init__(self, name, id=None):
        if id is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id
        self.name = name
        self.tests = []

    def to_dict(self):
        return {"id": self.id, "name": self.name, "tests": [test.to_dict() if hasattr(test, 'to_dict') else test.name for test in self.tests]}

    @classmethod
    def from_dict(cls, data):
        tests = []
        for test_data in data.get('tests', []):
            if hasattr(Test, 'from_dict'):
                tests.append(Test.from_dict(test_data))
            else:
                tests.append(Test(name=test_data.get('name'))) # Assuming test_data is a dictionary with 'name'
        return cls(name=data.get('name'), id=data.get('id'), tests=tests)
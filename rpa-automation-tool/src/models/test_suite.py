import uuid

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
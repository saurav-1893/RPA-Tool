from ..core.recorder import Recorder
import uuid

class Test:
    def __init__(self, name, id=None, steps=None, result=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.name = name
        self.steps = steps if steps is not None else []
        self.result = result
        self.is_recording = False
        self.recorder = Recorder()

    def record(self, steps=None):
        self.is_recording = True
        self.recorder.start_recording(self)
        self.steps = steps if steps is not None else []

    def stop_recording(self):
        self.is_recording = False
        self.steps = self.recorder.stop()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'steps': self.steps,
            'result': self.result,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name'),
            steps=data.get('steps', []),
            result=data.get('result'),
        )

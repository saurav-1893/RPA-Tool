from rpa_automation_tool.src.core.recorder import Recorder

class Test:
    def __init__(self, name, steps=None, result=None):
        self.name = name
        self.steps = steps if steps is not None else []
        self.result = result
        self.is_recording = False
        self.recorder = Recorder()

    def record(self):
        self.is_recording = True
        self.recorder.start_recording(self)

    def stop_recording(self):
        self.is_recording = False
        self.steps = self.recorder.stop()

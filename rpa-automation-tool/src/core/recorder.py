class Recorder:
    def __init__(self):
        self.is_recording = False
        self.recorded_steps = []

    def start_recording(self):
        self.is_recording = True
        self.recorded_steps = []  # Clear previous recording
        print("Recording started.")

    def stop_recording(self):
        self.is_recording = False
        print("Recording stopped.")

    def add_action(self, action_data):
        if self.is_recording:
            self.recorded_steps.append(action_data)
            print(f"Added action: {action_data}")
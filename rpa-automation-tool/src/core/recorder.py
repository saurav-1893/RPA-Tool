class Recorder:
    def __init__(self):
        self.is_recording = False
        self.current_test = None

    def start_recording(self, test):
        """
        Prepare the recorder for a new recording for a specific test.
        """
        self.is_recording = True
        self.current_test = test
        self.current_test.steps = []  # Clear previous steps in the test
        print("Recording started.")

    def stop_recording(self):
        self.is_recording = False
        print("Recording stopped.")
        return self.current_test.steps

    def add_action(self, action_data):
        if self.is_recording:
            self.current_test.steps.append(action_data)
            print(f"Added action to test: {action_data}")
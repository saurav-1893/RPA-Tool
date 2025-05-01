from pynput import mouse, keyboard
import time
from threading import Thread

class Recorder:
    def __init__(self):
        self.is_recording = False
        self.current_test = None
        self.steps = []
        self.mouse_listener = None
        self.keyboard_listener = None
        self.start_time = None

    def start_recording(self, test):
        """
        Prepare the recorder for a new recording for a specific test.
        """
        self.is_recording = True
        self.start_time = time.time()
        self.current_test = test
        self.current_test.steps = []  # Clear previous steps in the test
        print("Recording started.")

    def stop_recording(self):
        self.is_recording = False
        print("Recording stopped.")
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        return self.current_test.steps, self.current_test

    def _on_mouse_click(self, x, y, button, pressed):
        if pressed and self.is_recording:
            action_data = {
                "type": "mouse_click",
                "x": x,
                "y": y,
                "button": str(button),
                "time": time.time() - self.start_time
            }
            self.current_test.steps.append(action_data)
            print(f"Recorded mouse click: {action_data}")

    def _on_mouse_move(self, x, y):
        # Optionally record mouse movements, but can generate a lot of data
        # if self.is_recording:
        #     action_data = {
        #         "type": "mouse_move",
        #         "x": x,
        #         "y": y,
        #         "time": time.time() - self.start_time
        #     }
        #     self.current_test.steps.append(action_data)
        #     print(f"Recorded mouse move: {action_data}")
        pass # Not recording mouse move for now

    def _on_key_press(self, key):
        if self.is_recording:
            try:
                action_data = {
                    "type": "keyboard_press",
                    "key": key.char,
                    "time": time.time() - self.start_time
                }
            except AttributeError:
                action_data = {
                    "type": "keyboard_press",
                    "key": str(key),
                    "time": time.time() - self.start_time
                }
            self.current_test.steps.append(action_data)
            print(f"Recorded key press: {action_data}")

    def start_listeners(self):
        if self.is_recording:
            self.mouse_listener = mouse.Listener(
                on_click=self._on_mouse_click,
                on_move=self._on_mouse_move
            )
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press
            )
            self.mouse_listener.start()
            self.keyboard_listener.start()

    def start(self, test):
        self.start_recording(test)
        listener_thread = Thread(target=self.start_listeners)
        listener_thread.start()
import tkinter as tk
from tkinter import ttk

class RPAApp:
    def __init__(self, root):
        self.root = root
        root.title("RPA Automation Tool")

        self.create_menu()
        self.create_recording_section()
        self.create_playback_section()
        self.create_status_bar()

        self.is_recording = False
        self.recorded_actions = []

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def create_recording_section(self):
        recording_frame = ttk.LabelFrame(self.root, text="Recording")
        recording_frame.pack(fill=tk.BOTH, padx=10, pady=10)

        self.start_button = tk.Button(recording_frame, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=(0, 5))

        self.stop_button = tk.Button(recording_frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=(0, 5))

        self.add_action_button = tk.Button(recording_frame, text="Add new Action", command=self.add_action, state=tk.DISABLED)
        self.add_action_button.pack(pady=(0, 5))

        self.actions_listbox = tk.Listbox(recording_frame, height=10, width=50)
        self.actions_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

    def create_playback_section(self):
        playback_frame = ttk.LabelFrame(self.root, text="Playback")
        playback_frame.pack(fill=tk.BOTH, padx=10, pady=10)

        self.run_button = tk.Button(playback_frame, text="Run last Recording", command=self.run_recording, state=tk.DISABLED)
        self.run_button.pack(pady=(0, 5))

        self.pause_button = tk.Button(playback_frame, text="Pause", command=self.pause_recording, state=tk.DISABLED)
        self.pause_button.pack(pady=(0, 5))

        self.stop_playback_button = tk.Button(playback_frame, text="Stop", command=self.stop_playback, state=tk.DISABLED)
        self.stop_playback_button.pack(pady=(0, 5))

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def start_recording(self):
        self.status_var.set("Recording...")
        self.is_recording = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.add_action_button.config(state=tk.NORMAL)
        self.recorded_actions.clear()
        self.actions_listbox.delete(0, tk.END)
        self.run_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_playback_button.config(state=tk.DISABLED)
        print("Starting Recording...")
        # TODO: Implement recording logic

    def stop_recording(self):
        self.status_var.set("Ready")
        self.is_recording = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.add_action_button.config(state=tk.DISABLED)
        self.run_button.config(state=tk.NORMAL)
        print("Stopped Recording.")
        # TODO: Implement stop recording logic

    def add_action(self):
        if self.is_recording:
            action = f"Action {len(self.recorded_actions) + 1}"
            self.recorded_actions.append(action)
            self.actions_listbox.insert(tk.END, action)
            print("Add action")
        # TODO: Implement add new action logic

    def run_recording(self):
        self.status_var.set("Running...")
        self.run_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_playback_button.config(state=tk.NORMAL)
        print("Running the last recording...")
        # TODO: Implement playback logic

    def pause_recording(self):
        self.status_var.set("Paused")
        self.pause_button.config(state=tk.DISABLED)
        self.stop_playback_button.config(state=tk.NORMAL)
        self.run_button.config(state=tk.NORMAL)
        print("Pause recording")
        # TODO: Implement pause recording logic

    def stop_playback(self):
        self.status_var.set("Ready")
        self.pause_button.config(state=tk.DISABLED)
        self.stop_playback_button.config(state=tk.DISABLED)
        self.run_button.config(state=tk.NORMAL)
        print("Stop recording")
        # TODO: Implement stop recording logic
    
    def show_about(self):
        print("Show about")
        # TODO: show about logic

if __name__ == "__main__":
    root = tk.Tk()
    app = RPAApp(root)
    root.mainloop()
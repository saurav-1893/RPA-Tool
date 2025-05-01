import tkinter as tk

def on_start_button_click():
    print("Starting Recording...")
    # TODO: Implement recording logic

def on_run_button_click():
    print("Running the last recording...")
    # TODO: Implement playback logic

root = tk.Tk()
root.title("RPA Automation Tool")

label = tk.Label(root, text="Welcome to the RPA Tool!")
label.pack()

start_button = tk.Button(root, text="Start Recording", command=on_start_button_click)
start_button.pack()

run_button = tk.Button(root, text="Run last Recording", command=on_run_button_click)
run_button.pack()

root.mainloop()
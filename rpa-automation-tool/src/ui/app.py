print("RPA Automation Tool")
print("Welcome to the RPA Automation Tool!")

while True:
    print("\\nMenu:")
    print("1) Start recording")
    print("2) Run last recording")
    print("3) Exit")

    choice = input("Enter your choice: ")

    if choice == '1':
        print("starting recording...")
        # TODO: Implement recording logic
    elif choice == '2':
        print("Running the last recording...")
        # TODO: Implement playback logic
    elif choice == '3':
        break
    else:
        print("Wrong input")
# src/core/player.py
class Player:
    def play(self, test):
        print(f"Playing test: {test.name}")
        for step in test.steps:
            print(f"  Executing step: {step.description}")
            # Here you would add the actual logic to perform the step
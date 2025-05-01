class Test:
    def __init__(self, name, steps=None, result=None):
        self.name = name
        self.steps = steps if steps is not None else []
        self.result = result
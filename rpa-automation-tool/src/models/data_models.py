# src/models/data_models.py
from dataclasses import dataclass
@dataclass
class Project:
  name: str
  description: str
@dataclass
class Environment:
    name: str
    browser: str
    url: str
@dataclass
class TestSuite:
    name: str
    description: str
    project: Project
@dataclass
class TestCase:
    name: str
    description: str
    test_suite: TestSuite
    test_steps : list
@dataclass
class TestStep:
  description : str
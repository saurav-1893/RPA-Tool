from typing import List
from rpa_automation_tool.src.models.project import Project
from rpa_automation_tool.src.models.test import Test
from rpa_automation_tool.src.models.step import Step

class Runner:
    def run(self, project: Project) -> List[str]:
        results = []
        for test in project.tests:
            result = self._run_test(test)
            results.append(result)
        return results

    def _run_test(self, test: Test) -> str:
        
        test_result = "Passed"
        for step in test.steps:
            
            step_result = self._run_step(step)
            step.result = step_result
            if step_result != "Passed":
                test_result = "Failed"
        test.result = test_result

        return test_result
    
    def _run_step(self, step: Step) -> str:
        return "Passed"
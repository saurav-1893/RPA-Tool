// project_manager.js

class ProjectManager {
    constructor(currentPage) {
 this.currentPage = currentPage;
        this.projects = [];
        this.currentProject = null;
        this.currentTestSuite = null;
        this.loadProjects();
        this.setupEventListeners();
    }

    setupEventListeners() {
 switch (this.currentPage) {
 case 'index':
 const projectForm = document.getElementById('projectForm');
 if (projectForm) {
 projectForm.addEventListener('submit', this.handleProjectFormSubmit.bind(this));
 }
 break;
 case 'project':
 const testSuiteForm = document.getElementById('testSuiteForm');
 if (testSuiteForm) {
 testSuiteForm.addEventListener('submit', this.handleTestSuiteFormSubmit.bind(this));
 }
 break;
 case 'test_suite':
 const testForm = document.getElementById('testForm');
 if (testForm) {
 testForm.addEventListener('submit', this.handleTestFormSubmit.bind(this));
 }
 const recordButton = document.getElementById('recordButton');
 if (recordButton) {
 recordButton.addEventListener('click', this.handleRecordButtonClick.bind(this));
 }
 const playButton = document.getElementById('playButton');
 if (playButton) {
 playButton.addEventListener('click', this.handlePlayButtonClick.bind(this));
 }
 break;
        }
    }

    handleProjectFormSubmit(event) {
        event.preventDefault();
        const projectName = document.getElementById('projectName').value;
 if (projectName.trim()) {
 this.createProject(projectName.trim());
        }
    }

    handleTestSuiteFormSubmit(event) {
        event.preventDefault();
        const testSuiteName = document.getElementById('testSuiteName').value;
 if (testSuiteName.trim()) {
 this.createTestSuite(testSuiteName.trim());
        }
    }

    handleTestFormSubmit(event) {
        event.preventDefault();
        const testName = document.getElementById('testName').value;
 if (testName.trim()) {
 this.createTest(testName.trim());
 }
    }

    handleRecordButtonClick() {
 const recordButton = document.getElementById('recordButton');
 if (recordButton.textContent === 'Start Recording') {
 this.startRecording();
 recordButton.textContent = 'Stop Recording';
        } else {
 this.stopRecording();
 recordButton.textContent = 'Start Recording';
        }
    }

 handlePlayButtonClick() {
        // Assuming you have a way to select the current test on the test_suite page
        this.playTest(this.currentTest.id);
    }

    handleRunTestButtonClick(testId) {
 this.runTest(testId);
    }

    loadProjects() {
        fetch('/api/projects')
            .then(response => response.json())
            .then(data => {
 if (this.currentPage === 'index') {
 this.projects = data;
 this.renderProjects(data);
 } else if (this.currentPage === 'project') {
 const projectId = window.location.pathname.split('/')[2];
 this.currentProject = data.find(project => project.id === projectId);
 if (this.currentProject) {
 this.renderTestSuites(this.currentProject.test_suites);
 }
 } else if (this.currentPage === 'test_suite') {
 const projectId = window.location.pathname.split('/')[2];
 const suiteId = window.location.pathname.split('/')[4];
 this.currentProject = data.find(project => project.id === projectId);
 if (this.currentProject) {
 this.currentTestSuite = this.currentProject.test_suites.find(suite => suite.id === suiteId);
 if (this.currentTestSuite) {
 this.renderTests(this.currentTestSuite.tests);
 }
 }
 }
            });
    }

    createProject(projectName) {
        fetch('/api/projects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: projectName })
        })
            .then(response => response.json())
            .then(() => {
 window.location.reload();
            });
    }

    createTestSuite(testSuiteName) {
        if (this.currentProject) {
            fetch(`/api/projects/${this.currentProject.id}/suites`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: testSuiteName })
            }).then(() => {
 // Reload the page to see the new test suite
                    this.renderTestSuites();
                });
        }
    }

    createTest(testName) {
        if (this.currentProject && this.currentTestSuite) {
            fetch(`/api/projects/${this.currentProject.id}/suites/${this.currentTestSuite.id}/tests`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: testName })
            }).then(() => {
 // Reload the page to see the new test
                    this.renderTests();
                });
        }
    }

    selectProject(project) {
        this.currentProject = project;
        this.renderProject();
    }

    selectTestSuite(testSuite) {
        this.currentTestSuite = testSuite;
        this.renderTests();
    }

    startRecording() {
 if (this.currentProject && this.currentTestSuite) {
            fetch(`/api/projects/${this.currentProject.id}/suites/${this.currentTestSuite.id}/tests/${this.currentTest.id}/record/start`, {
                method: 'POST'
            })
 .then(response => response.json())
 .then(data => console.log('Recording started:', data))
 .catch(error => console.error('Error starting recording:', error));
 }
    }

    stopRecording() {
 if (this.currentProject && this.currentTestSuite) {
            fetch(`/api/projects/${this.currentProject.id}/suites/${this.currentTestSuite.id}/tests/${this.currentTest.id}/record/stop`, {
                method: 'POST'
            })
 .then(response => response.json())
 .then(data => {
 console.log('Recording stopped:', data);
 // Optionally, update the test steps in the UI
 })
 .catch(error => console.error('Error stopping recording:', error));
 }
    }

    playTest(testId) {
 if (this.currentProject && this.currentTestSuite) {
            fetch(`/api/projects/${this.currentProject.id}/suites/${this.currentTestSuite.id}/tests/${testId}/play`, {
                method: 'POST'
            })
 .then(response => response.json())
 .then(data => {
 console.log('Test played:', data);
 // Optionally, provide feedback in the UI about playback status
 })
 .catch(error => console.error('Error playing test:', error));
 }
    }
    runTest(testId) {
 if (this.currentProject && this.currentTestSuite) {
            fetch(`/api/projects/${this.currentProject.id}/suites/${this.currentTestSuite.id}/tests/${testId}/run`, {
                method: 'POST'
            })
 .then(response => response.json())
 .then(data => console.log('Test run result:', data))
 .catch(error => console.error('Error running test:', error));
 }
    }

 renderProjects(projects) {
        const projectList = document.getElementById('projectList');
        if (projectList) {
            projectList.innerHTML = '';
 projects.forEach(project => {
                const projectItem = document.createElement('li');
                const link = document.createElement('a');
                link.textContent = project.name;
                link.href = `/project/${project.id}`;
                projectItem.appendChild(link);
                projectList.appendChild(projectItem);
            });
        }
    }

 renderTestSuites(testSuites) {
        const testSuiteList = document.getElementById('testSuiteList');
        if (testSuiteList) {
            testSuiteList.innerHTML = '';
 testSuites.forEach(testSuite => {
                const testSuiteItem = document.createElement('li');
                const link = document.createElement('a');
                link.textContent = testSuite.name;
                link.href = `/project/${this.currentProject.id}/suite/${testSuite.id}`;
                testSuiteItem.appendChild(link);
                testSuiteList.appendChild(testSuiteItem);
            });
        }
    }

 renderTests(tests) {
 const testList = document.getElementById('testList');
 if (testList) {
 // You'll need to update this part to render tests appropriately
 }

    }
}
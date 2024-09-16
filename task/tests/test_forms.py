from django.test import TestCase
from task.models import Worker, Team, Project, Task, TaskType, Position
from task.forms import (
    WorkerCreateForm,
    WorkerUpdateForm,
    TaskForm,
    ProjectForm,
    SearchByUsername,
    SearchByName,
    SearchByPriority
)


class WorkerCreateFormTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.team1 = Team.objects.create(name="Team 1")
        self.team2 = Team.objects.create(name="Team 2")

    def test_valid_form(self):
        form_data = {
            "username": "worker1",
            "password1": "password123",
            "password2": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "position": self.position.id,
            "teams": [self.team1.id, self.team2.id],
        }
        form = WorkerCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            "username": "worker1",
            "password1": "password123",
            "password2": "wrongpassword",
            "first_name": "John",
            "last_name": "Doe",
            "position": self.position.id,
            "teams": [self.team1.id, self.team2.id],
        }
        form = WorkerCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


class WorkerUpdateFormTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.team1 = Team.objects.create(name="Team 1")
        self.team2 = Team.objects.create(name="Team 2")
        self.project1 = Project.objects.create(
            name="Project 1",
            description="Description 1",
        )
        self.project2 = Project.objects.create(
            name="Project 2",
            description="Description 2",
        )
        self.worker = Worker.objects.create(
            username="worker1",
            first_name="John",
            last_name="Doe",
            position=self.position,
        )
        self.worker.teams.set([self.team1, self.team2])
        self.worker.projects.set([self.project1])

    def test_form_with_invalid_projects(self):
        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "position": self.position.id,
            "teams": [self.team1.id],
            "projects": [self.project2.id],
        }
        form = WorkerUpdateForm(instance=self.worker, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("projects", form.errors)

    def test_form_save(self):
        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "position": self.position.id,
            "teams": [self.team1.id],
            "projects": [self.project1.id],
        }
        form = WorkerUpdateForm(instance=self.worker, data=form_data)
        if form.is_valid():
            worker = form.save(commit=False)
            worker.save()
            form.save_m2m()

        self.worker.refresh_from_db()
        self.assertEqual(set(self.worker.projects.all()), {self.project1})


class TaskFormTest(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="Bug")
        self.position = Position.objects.create(name="Developer")
        self.worker = Worker.objects.create(
            username="worker1",
            first_name="John",
            last_name="Doe",
            position=self.position,
        )
        self.project = Project.objects.create(
            name="Project 1",
            description="Description of Project 1",
        )
        self.task = Task.objects.create(
            name="Task 1",
            description="Description of Task 1",
            deadline="2024-09-30",
            priority="Low",
            task_type=self.task_type,
            project=self.project
        )

    def test_form_with_project(self):
        form_data = {
            "name": "Task 2",
            "description": "Description of Task 2",
            "deadline": "2024-09-30",
            "priority": "High",
            "task_type": self.task_type.id,
            "assignees": [self.worker.id],
            "project": self.project.id,
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_without_project(self):
        form_data = {
            "name": "Task 2",
            "description": "Description of Task 2",
            "deadline": "2024-09-30",
            "priority": "High",
            "task_type": self.task_type.id,
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())


class ProjectFormTest(TestCase):
    def setUp(self):
        self.team1 = Team.objects.create(name="Team 1")
        self.team2 = Team.objects.create(name="Team 2")

    def test_valid_form(self):
        form_data = {
            "name": "Project 1",
            "description": "Description of Project 1",
            "teams": [self.team1.id, self.team2.id],
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            "name": "",
            "description": "Description of Project 1",
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class SearchFormTest(TestCase):
    def test_search_by_username_valid(self):
        form_data = {"username": "testuser"}
        form = SearchByUsername(data=form_data)
        self.assertTrue(form.is_valid())

    def test_search_by_name_valid(self):
        form_data = {"name": "John Doe"}
        form = SearchByName(data=form_data)
        self.assertTrue(form.is_valid())

    def test_search_by_priority_valid(self):
        form_data = {"priority": "High"}
        form = SearchByPriority(data=form_data)
        self.assertTrue(form.is_valid())

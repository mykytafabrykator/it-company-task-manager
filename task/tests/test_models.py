from django.test import TestCase
from django.urls import reverse
from task.models import TaskType, Position, Project, Team, Task
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskTypeModelTest(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="Development")

    def test_str_method(self):
        self.assertEqual(str(self.task_type), "Development")

    def test_meta_ordering(self):
        self.assertEqual(TaskType._meta.ordering, ["name"])


class PositionModelTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")

    def test_str_method(self):
        self.assertEqual(str(self.position), "Developer")

    def test_get_absolute_url(self):
        self.assertEqual(
            self.position.get_absolute_url(),
            reverse("task:position-detail", kwargs={"pk": self.position.pk}),
        )

    def test_meta_ordering(self):
        self.assertEqual(Position._meta.ordering, ["name"])


class WorkerModelTest(TestCase):
    username = "worker1"
    password = "password123"
    first_name = "John"
    last_name = "Doe"
    position = "Developer"

    def setUp(self):
        self.position = Position.objects.create(name=self.position)
        self.worker = User.objects.create_user(
            username=self.username,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name,
            position=self.position
        )

    def test_str_method(self):
        self.assertEqual(str(self.worker), "John Doe")

    def test_get_absolute_url(self):
        self.assertEqual(
            self.worker.get_absolute_url(),
            reverse("task:worker-detail", kwargs={"pk": self.worker.pk}),
        )

    def test_worker_creation(self) -> None:
        self.assertEqual(self.worker.username, self.username)
        self.assertEqual(self.worker.position, self.position)
        self.assertTrue(self.worker.check_password(self.password))


class ProjectModelTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.worker = User.objects.create_user(
            username="worker1",
            password="password123",
            first_name="John",
            last_name="Doe",
            position=self.position
        )
        self.project = Project.objects.create(
            name="Project 1",
            description="Test Project",
        )

    def test_str_method(self):
        self.assertEqual(str(self.project), "Project 1")

    def test_get_absolute_url(self):
        self.assertEqual(
            self.project.get_absolute_url(),
            reverse("task:project-detail", kwargs={"pk": self.project.pk}),
        )

    def test_meta_ordering(self):
        self.assertEqual(Project._meta.ordering, ["name"])


class TeamModelTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.worker = User.objects.create_user(
            username="worker1",
            password="password123",
            first_name="John",
            last_name="Doe",
            position=self.position
        )
        self.project = Project.objects.create(
            name="Project 1",
            description="Test Project",
        )
        self.team = Team.objects.create(name="Team 1")
        self.team.workers.add(self.worker)
        self.team.projects.add(self.project)

    def test_str_method(self):
        self.assertEqual(str(self.team), "Team 1")

    def test_get_absolute_url(self):
        self.assertEqual(
            self.team.get_absolute_url(),
            reverse("task:team-detail", kwargs={"pk": self.team.pk}),
        )

    def test_delete_method(self):
        self.team.delete()

        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())


class TaskModelTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.worker = User.objects.create_user(
            username="worker1",
            password="password123",
            first_name="John",
            last_name="Doe",
            position=self.position
        )
        self.project = Project.objects.create(
            name="Project 1",
            description="Test Project",
        )
        self.task_type = TaskType.objects.create(name="Development")
        self.task = Task.objects.create(
            name="Task 1",
            description="Test Task",
            deadline="2024-12-31",
            is_completed=False,
            priority="HIGH",
            task_type=self.task_type,
            project=self.project
        )
        self.task.assignees.add(self.worker)

    def test_str_method(self):
        self.assertEqual(str(self.task), "Task 1 (deadline: 2024-12-31)")

    def test_meta_ordering(self):
        self.assertEqual(Task._meta.ordering, ["is_completed"])

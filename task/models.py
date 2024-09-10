from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

PRIORITY_CHOICES = [
    ("URGENT", "Urgent"),
    ("HIGH", "High"),
    ("MEDIUM", "Medium"),
    ("LOW", "Low"),
]


class TaskType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("task:position-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name="workers",
        null=True,
        blank=True,
    )

    def get_absolute_url(self):
        return reverse("task:worker-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    workers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="projects",
        blank=True,
    )

    def get_absolute_url(self):
        return reverse("task:project-detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=255)
    workers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="teams",
        blank=True,
    )
    projects = models.ManyToManyField(
        Project,
        related_name="teams",
        blank=True,
    )

    def get_absolute_url(self):
        return reverse("task:team-detail", kwargs={"pk": self.pk})

    def delete(self, *args, **kwargs):
        related_projects = list(self.projects.all())

        super().delete(*args, **kwargs)

        for project in related_projects:
            if project.teams.count() == 0:
                project.delete()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)

    priority = models.CharField(
        max_length=9,
        choices=PRIORITY_CHOICES,
        default="Low",
    )

    task_type = models.ForeignKey(
        TaskType,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="assigned_tasks",
        blank=True,
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    class Meta:
        ordering = ["is_completed"]

    def __str__(self):
        return f"{self.name} (deadline: {self.deadline})"

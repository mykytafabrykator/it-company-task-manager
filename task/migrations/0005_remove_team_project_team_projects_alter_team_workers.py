# Generated by Django 5.1.1 on 2024-09-09 06:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("task", "0004_remove_project_team_team_project"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="team",
            name="project",
        ),
        migrations.AddField(
            model_name="team",
            name="projects",
            field=models.ManyToManyField(
                blank=True, null=True, related_name="teams", to="task.project"
            ),
        ),
        migrations.AlterField(
            model_name="team",
            name="workers",
            field=models.ManyToManyField(
                blank=True, null=True, related_name="teams", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]

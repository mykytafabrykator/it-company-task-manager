from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from task.models import Team, Worker, Project, Task


@receiver(m2m_changed, sender=Team.projects.through)
def handle_project_removal_from_team(sender, instance, action, pk_set, **kwargs):
    if action == "post_remove":
        removed_projects = set(pk_set)
        for project_id in removed_projects:
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                continue

            workers_to_update = Worker.objects.filter(projects=project)
            for worker in workers_to_update:
                worker.projects.remove(project)

            tasks_to_update = Task.objects.filter(project=project)
            for task in tasks_to_update:
                for worker in task.assignees.all():
                    if worker in workers_to_update:
                        task.assignees.remove(worker)

            if not project.teams.exists():
                project.delete()

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from task.models import Team, Worker, Project, Task


@receiver(m2m_changed, sender=Team.projects.through)
def update_worker_projects_on_team_project_change(sender, instance, action, pk_set, **kwargs):
    if action == "post_remove":
        removed_projects = set(pk_set)
        for project_id in removed_projects:
            project = Project.objects.get(id=project_id)
            if not project.teams.exists():
                for worker in project.workers.all():
                    worker.projects.remove(project)



@receiver(m2m_changed, sender=Project.workers.through)
def remove_worker_from_tasks_on_project(sender, instance,
                                        action, pk_set, **kwargs):

    if action == "post_remove":
        workers_removed = Worker.objects.filter(pk__in=pk_set)

        for worker in workers_removed:
            tasks = Task.objects.filter(project=instance, assignees=worker)
            for task in tasks:
                task.assignees.remove(worker)

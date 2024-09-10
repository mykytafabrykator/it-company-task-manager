from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from task.models import Team, Worker, Project, Task


@receiver(m2m_changed, sender=Team.workers.through)
def update_worker_projects_and_tasks(sender, instance, action, reverse, model, pk_set, **kwargs):

    if action == "post_remove":
        workers_removed = Worker.objects.filter(pk__in=pk_set)

        for worker in workers_removed:
            related_projects = instance.projects.all()

            for project in related_projects:
                worker_teams_in_project = Team.objects.filter(projects=project, workers=worker)

                if not worker_teams_in_project.exists():
                    project.workers.remove(worker)

                    tasks = Task.objects.filter(project=project, assignees=worker)
                    for task in tasks:
                        task.assignees.remove(worker)


@receiver(m2m_changed, sender=Project.workers.through)
def remove_worker_from_tasks_on_project(sender, instance, action, reverse, model, pk_set, **kwargs):

    if action == "post_remove":
        workers_removed = Worker.objects.filter(pk__in=pk_set)

        for worker in workers_removed:
            tasks = Task.objects.filter(project=instance, assignees=worker)
            for task in tasks:
                task.assignees.remove(worker)

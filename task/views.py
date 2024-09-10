from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from task.forms import (
    WorkerCreateForm,
    WorkerUpdateForm,
    TaskForm,
    ProjectForm,
    TeamForm,
)
from task.models import Worker, Project, Team, Position, TaskType, Task


@login_required
def index(request):
    """View function for the home page of the site."""

    context = {
        "num_workers": Worker.objects.count(),
        "num_projects": Project.objects.count(),
        "num_teams": Team.objects.count(),
        "num_positions": Position.objects.count(),
        "num_task_types": TaskType.objects.count(),
    }

    return render(request, "task/index.html", context=context)


class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = Worker
    paginate_by = 5

    def get_queryset(self):
        return Worker.objects.select_related("position") \
            .prefetch_related(
                "teams__projects",
                "projects",
            ).order_by("username")


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker

    def get_queryset(self):
        return Worker.objects.select_related("position") \
            .prefetch_related(
                "teams__projects",
                "projects",
                "assigned_tasks__project",
            )


class WorkerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    form_class = WorkerUpdateForm

    def get_object(self, queryset=None):
        return get_object_or_404(
            Worker.objects.select_related("position")
            .prefetch_related("teams", "projects"),
            pk=self.kwargs["pk"]
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        worker = form.instance
        selected_teams = form.cleaned_data["teams"]
        selected_projects = form.cleaned_data["projects"]

        worker.teams.set(selected_teams)

        worker.projects.set(selected_projects)

        return response


class WorkerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Worker
    success_url = reverse_lazy("task:worker-list")

    def get_object(self, queryset=None):
        return get_object_or_404(
            Worker.objects.select_related("position")
            .prefetch_related("teams"),
            pk=self.kwargs["pk"]
        )


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Worker
    form_class = WorkerCreateForm

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.teams.set(form.cleaned_data["teams"])
        return response


class PositionListView(LoginRequiredMixin, generic.ListView):
    model = Position
    paginate_by = 5


class PositionDetailView(LoginRequiredMixin, generic.DetailView):
    model = Position


class PositionCreateView(LoginRequiredMixin, generic.CreateView):
    model = Position
    fields = "__all__"


class PositionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Position
    fields = "__all__"


class PositionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Position
    success_url = reverse_lazy("task:position-list")


class TeamListView(LoginRequiredMixin, generic.ListView):
    model = Team
    paginate_by = 5


class TeamCreateView(LoginRequiredMixin, generic.CreateView):
    model = Team
    form_class = TeamForm


class TeamDetailView(LoginRequiredMixin, generic.DetailView):
    model = Team


class TeamUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Team
    form_class = TeamForm


class TeamDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Team
    success_url = reverse_lazy("task:team-list")


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    paginate_by = 5


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project

    def get_queryset(self):
        return Project.objects.prefetch_related("teams__workers").all()


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy("task:project-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.teams.set(form.cleaned_data["teams"])
        return response


class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Project
    fields = ("name", "description",)
    success_url = reverse_lazy("task:project-list")


class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    success_url = reverse_lazy("task:project-list")


class TaskTypeListView(LoginRequiredMixin, generic.ListView):
    model = TaskType
    paginate_by = 5
    context_object_name = "task_type_list"
    template_name = "task/task_type_list.html"


class TaskTypeDetailView(LoginRequiredMixin, generic.DetailView):
    model = TaskType
    template_name = "task/task_type_detail.html"
    context_object_name = "task_type"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = Task.objects.filter(task_type=self.object)
        return context


class TaskTypeCreateView(LoginRequiredMixin, generic.CreateView):
    model = TaskType
    fields = ("name", )
    template_name = "task/task_type_form.html"
    success_url = reverse_lazy("task:task-type-list")


class TaskTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = TaskType
    fields = ("name", )
    template_name = "task/task_type_form.html"
    success_url = reverse_lazy("task:task-type-list")


class TaskTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = TaskType
    template_name = "task/task_type_confirm_delete.html"
    context_object_name = "task_type"
    success_url = reverse_lazy("task:task-type-list")


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task

    def get_queryset(self):
        return (Task.objects.all()
                .select_related("project")
                .prefetch_related("assignees"))


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task

    def get_queryset(self):
        return (Task.objects.select_related("project")
                .prefetch_related("assignees"))


class TaskCreateView(generic.CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("task:task-list")


class TaskUpdateView(generic.UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("task:task-list")


class TaskDeleteView(generic.DeleteView):
    model = Task
    success_url = reverse_lazy("task:task-list")


@login_required
def toggle_task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.user in task.project.workers.all():
        task.is_completed = not task.is_completed
        task.save()
    else:
        messages.error(
            request,
            "You are not part of the project "
            "associated with this task, so "
            "you cannot assign yourself to it."
        )
    return redirect("task:task-detail", pk=task.pk)


@login_required
def toggle_task_assign(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.user in task.project.workers.all():
        if request.user in task.assignees.all():
            task.assignees.remove(request.user)
        else:
            task.assignees.add(request.user)
        task.save()
    else:
        messages.error(
            request,
            "You are not part of the project "
            "associated with this task, so "
            "you cannot assign yourself to it."
        )
    return redirect("task:task-detail", pk=task.pk)

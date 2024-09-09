from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from task.forms import WorkerCreateForm, WorkerUpdateForm, TeamUpdateForm
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
    queryset = (Worker.objects.all()
                .select_related("position")
                .prefetch_related("teams__projects")
                .order_by("username"))
    paginate_by = 5


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker
    queryset = (Worker.objects.all()
                .select_related("position")
                .prefetch_related("teams__projects")
                .order_by("username"))


class WorkerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    form_class = WorkerUpdateForm

    def get_object(self, queryset=None):
        return get_object_or_404(
            Worker.objects.select_related("position")
            .prefetch_related("teams"),
            pk=self.kwargs["pk"]
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.teams.set(form.cleaned_data["teams"])
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
    fields = ("name", "workers", "projects", )
    success_url = reverse_lazy("task:team-list")


class TeamDetailView(LoginRequiredMixin, generic.DetailView):
    model = Team


class TeamUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Team
    form_class = TeamUpdateForm


class TeamDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Team
    success_url = reverse_lazy("task:team-list")


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    paginate_by = 5


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project

    def get_queryset(self):
        return Project.objects.prefetch_related('teams__workers').all()


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    fields = "__all__"
    success_url = reverse_lazy("task:project-list")


class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Project
    fields = "__all__"


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

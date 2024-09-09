from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from task.forms import WorkerCreateForm, WorkerUpdateForm
from task.models import Worker, Project, Team, Position


@login_required
def index(request):
    """View function for the home page of the site."""

    context = {
        "num_workers": Worker.objects.count(),
        "num_projects": Project.objects.count(),
        "num_teams": Team.objects.count(),
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

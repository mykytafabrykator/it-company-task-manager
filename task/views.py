from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from task.forms import WorkerCreateForm, WorkerUpdateForm
from task.models import Worker, Project, Team


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

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.teams.set(form.cleaned_data["teams"])
        return response


class WorkerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Worker
    success_url = reverse_lazy("task:worker-list")


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Worker
    form_class = WorkerCreateForm

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.teams.set(form.cleaned_data["teams"])
        return response

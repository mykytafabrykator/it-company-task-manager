from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from task.models import Worker, Team, Project, Task


class WorkerCreateForm(UserCreationForm):
    teams = forms.ModelMultipleChoiceField(
        queryset=Team.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "position",
            "teams",
        )


class WorkerUpdateForm(UserChangeForm):
    teams = forms.ModelMultipleChoiceField(
        queryset=Team.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Worker
        fields = (
            "first_name",
            "last_name",
            "position",
            "teams",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "password" in self.fields:
            del self.fields["password"]


class TeamForm(forms.ModelForm):
    projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    workers = forms.ModelMultipleChoiceField(
        queryset=Worker.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Team
        fields = ("name", "workers", "projects",)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("name", "description",
                  "deadline", "priority",
                  "task_type", "assignees",
                  "project", )
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
            "assignees": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["assignees"].queryset = (
                Worker.objects.filter(projects=self.instance.project)
            )
        elif "project" in self.data:
            try:
                project_id = int(self.data.get("project"))
                self.fields["assignees"].queryset = (
                    Worker.objects.filter(projects=project_id)
                )
            except (ValueError, TypeError):
                self.fields["assignees"].queryset = Worker.objects.none()
        else:
            self.fields.pop("assignees")


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        widgets = {
            "workers": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        if project:
            teams = project.teams.all()
            valid_workers = Worker.objects.filter(teams__in=teams).distinct()

            self.fields["workers"].queryset = valid_workers

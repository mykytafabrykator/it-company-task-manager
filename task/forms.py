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

    projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.none(),
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
            "projects",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        worker = kwargs.get("instance")

        if worker:
            self.fields["teams"].initial = worker.teams.all()
            self.update_projects_field(worker)

        if "password" in self.fields:
            del self.fields["password"]

    def update_projects_field(self, worker):
        selected_teams = worker.teams.all()

        if selected_teams.exists():
            team_projects = (Project.objects
                             .filter(teams__in=selected_teams).distinct())

            if team_projects.exists():
                self.fields["projects"].queryset = team_projects
                self.fields["projects"].initial = (
                    worker.projects.filter(teams__in=selected_teams).distinct()
                )
            else:
                self.fields["projects"].widget = forms.TextInput(
                    attrs={
                        "readonly": "readonly",
                        "placeholder": "For associated "
                                       "teams there are no projects"
                    }
                )
                self.fields["projects"].label = "Projects"
        else:
            self.fields["projects"].widget = forms.TextInput(
                attrs={
                    "readonly": "readonly",
                    "placeholder": "Select and submit a team first"
                }
            )
            self.fields["projects"].label = "Projects"

    def clean(self):
        cleaned_data = super().clean()
        selected_teams = cleaned_data.get("teams")

        selected_projects = cleaned_data.get("projects")
        valid_projects = (
            Project.objects.filter(teams__in=selected_teams).distinct()
        )

        if selected_projects:
            for project in selected_projects:
                if project not in valid_projects:
                    self.add_error(
                        "projects",
                        f"Project '{project}' "
                        "does not belong to the selected teams."
                    )

        return cleaned_data

    def save(self, commit=True):
        worker = super().save(commit=False)
        current_projects = set(worker.projects.all())
        selected_projects = set(self.cleaned_data.get("projects"))

        removed_projects = current_projects - selected_projects

        if removed_projects:
            tasks_to_update = (
                Task.objects
                .filter(project__in=removed_projects, assignees=worker)
            )
            for task in tasks_to_update:
                task.assignees.remove(worker)

        if commit:
            worker.save()
            self.save_m2m()

        return worker


class TeamForm(forms.ModelForm):
    projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Team
        fields = ("name", "projects",)


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
    teams = forms.ModelMultipleChoiceField(
        queryset=Team.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Project
        fields = ("name", "description", "teams", )
        widgets = {
            "teams": forms.CheckboxSelectMultiple,
        }


class WorkerSearchForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by username"}),
    )


class TeamSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by name"}),
    )

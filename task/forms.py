from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from task.models import Worker, Team, Project


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


class TeamUpdateForm(forms.ModelForm):
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

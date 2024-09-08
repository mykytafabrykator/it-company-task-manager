from django.contrib.auth.forms import UserCreationForm
from django import forms

from task.models import Worker, Team


class WorkerForm(UserCreationForm):
    teams = forms.ModelMultipleChoiceField(
        queryset=Team.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,  # You can customize this widget
    )

    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "position",
            "teams",
        )
from django import forms
from .models import Task


class TaskCreateForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    end_time = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    class Meta:
        model = Task
        fields = ["title", "description", "start_time", "end_time", "location"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter Title"}
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter Location"}
            ),
        }

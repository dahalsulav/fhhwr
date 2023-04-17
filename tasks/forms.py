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
    hourly_rate = forms.DecimalField(
        disabled=True,
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "readonly": "readonly"}
        ),
    )

    total_cost = forms.DecimalField(
        disabled=True,
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "readonly": "readonly"}
        ),
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "start_time",
            "end_time",
            "location",
            "hourly_rate",
            "total_cost",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter Title"}
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter Location"}
            ),
        }


class TaskStatusUpdateForm(forms.ModelForm):
    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("in-progress", "In Progress"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
    ]

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=True)

    class Meta:
        model = Task
        fields = ["status"]
        labels = {"status": "Status"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the current status of the task
        current_status = self.instance.status
        # Define the valid status transitions
        valid_transitions = {
            "requested": ["in-progress", "rejected"],
            "in-progress": ["completed"],
        }
        # Update the choices for the status field based on the current status
        self.fields["status"].choices = [
            (choice, label)
            for choice, label in self.fields["status"].choices
            if choice in valid_transitions[current_status]
        ]

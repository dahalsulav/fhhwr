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

    def __init__(self, *args, **kwargs):
        super(TaskCreateForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True


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

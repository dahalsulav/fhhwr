from datetime import datetime
from django import forms
from django.utils.translation import gettext_lazy as _
from tasks.models import Task, TaskRequest
from users.models import Worker


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "start_time", "end_time"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
        labels = {
            "title": _("Title"),
            "description": _("Description"),
            "start_time": _("Start Time"),
            "end_time": _("End Time"),
        }

    def __init__(self, worker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker = worker

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError(_("Start time must be before end time."))

            # Calculate payment
            time_delta = end_time - start_time
            hours = time_delta.total_seconds() / 3600
            payment = round(hours * self.worker.hourly_rate, 2)
            cleaned_data["payment"] = payment

            # Check worker availability
            overlapping_tasks = Task.objects.filter(
                worker=self.worker,
                start_time__lt=end_time,
                end_time__gt=start_time,
                status__in=["requested", "in-progress"],
            )

            if overlapping_tasks.exists():
                raise ValidationError(
                    _(
                        "This worker is not available at the requested time. Please choose a different time."
                    )
                )

        return cleaned_data


class TaskRequestCreateForm(forms.ModelForm):
    class Meta:
        model = TaskRequest
        fields = ["task"]
        labels = {"task": _("Task")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["task"].widget = forms.HiddenInput()
        self.fields["task"].required = False

        for field in Task._meta.fields:
            if field.name not in ["id", "worker", "status"]:
                self.fields[field.name] = forms.CharField(
                    widget=forms.TextInput(attrs={"readonly": True}),
                    initial=getattr(self.instance.task, field.name),
                    label=field.verbose_name.title(),
                )

        self.fields["description"].widget = forms.Textarea()


class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "start_time",
            "end_time",
            "location",
            "worker",
            "status",
        ]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
        labels = {
            "title": _("Title"),
            "description": _("Description"),
            "start_time": _("Start Time"),
            "end_time": _("End Time"),
            "location": _("Location"),
            "worker": _("Assigned Worker"),
            "status": _("Status"),
        }
        help_texts = {
            "status": _(
                "Choose 'requested' to request the task, 'in-progress' to mark the task as in-progress, 'completed' to mark the task as completed, and 'rejected' to reject the task."
            ),
        }


class TaskRequestUpdateForm(forms.ModelForm):
    class Meta:
        model = TaskRequest
        fields = ["status"]
        labels = {"status": "Task status"}
        help_texts = {
            "status": "Select the current status of the task request.",
        }
        widgets = {"status": forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ]


class WorkerSearchForm(forms.Form):
    query = forms.CharField(label="Search for workers", max_length=255)

    def search(self):
        query = self.cleaned_data.get("query")
        if query:
            search_words = query.split()
            workers = Worker.objects.filter(
                availability=True,
                skills__name__icontains=search_words[0],
            )
            for word in search_words[1:]:
                workers = workers.filter(skills__name__icontains=word)
            return workers
        else:
            return Worker.objects.none()

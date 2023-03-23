from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import Customer, Worker


class Task(models.Model):
    STATUS_CHOICES = [
        ("requested", _("Requested")),
        ("in-progress", _("In Progress")),
        ("completed", _("Completed")),
        ("rejected", _("Rejected")),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="tasks"
    )
    worker = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="requested"
    )
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)


class TaskRequest(models.Model):
    STATUS_CHOICES = [
        ("requested", _("Requested")),
        ("accepted", _("Accepted")),
        ("rejected", _("Rejected")),
    ]
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="task_requests"
    )
    worker = models.ForeignKey(
        Worker, on_delete=models.CASCADE, related_name="task_requests"
    )
    requested_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="requested"
    )

    class Meta:
        unique_together = ("task", "worker")

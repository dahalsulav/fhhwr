from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib.auth.models import Group
from .models import Task
from .forms import TaskCreateForm, TaskStatusUpdateForm
from users.models import Worker
from django.utils.decorators import method_decorator
from django.core import serializers


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "tasks/task_create.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        worker = Worker.objects.get(pk=self.kwargs["pk"])
        form.fields["hourly_rate"].initial = worker.hourly_rate
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        worker = get_object_or_404(Worker, pk=self.kwargs["pk"])
        in_progress_tasks = Task.objects.filter(worker=worker, status="in-progress")
        in_progress_tasks_json = serializers.serialize("json", in_progress_tasks)
        context["in_progress_tasks_json"] = in_progress_tasks_json
        print(context["in_progress_tasks_json"])
        return context

    def form_valid(self, form):
        task = form.save(commit=False)
        task.customer = self.request.user.customer
        task.worker = Worker.objects.get(pk=self.kwargs["pk"])
        task.hourly_rate = form.cleaned_data["hourly_rate"]
        task.total_cost = form.cleaned_data["total_cost"]
        task.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("users:home")


def is_worker(user):
    return user.is_authenticated and user.is_worker


@method_decorator(user_passes_test(is_worker), name="dispatch")
class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskStatusUpdateForm
    template_name = "tasks/task_update.html"
    success_url = reverse_lazy("tasks:task_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        task = self.get_object()
        if self.request.GET.get("from_requested") == "true":
            # If called from requested status, show only in-progress and rejected options
            form.fields["status"].choices = [
                ("in-progress", "In Progress"),
                ("rejected", "Rejected"),
            ]
        elif task.status == "in-progress":
            # If called from in-progress status, show only completed option
            form.fields["status"].choices = [("completed", "Completed")]
        return form

    def form_valid(self, form):
        task = form.save(commit=False)
        task.save()
        messages.success(self.request, _("Task status updated successfully."))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        if task.status == "completed":
            context["show_update_status"] = False
        else:
            context["show_update_status"] = True
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        user = self.request.user
        if user.is_customer:
            tasks = Task.objects.filter(customer=user.customer).order_by(
                "-created_time"
            )
        elif user.is_worker:
            tasks = Task.objects.filter(worker=user.worker).order_by("-created_time")
        else:
            tasks = Task.objects.none()
        return tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_customer:
            customer = user.customer
            context["requested_tasks"] = Task.objects.filter(
                customer=customer, status="requested"
            )
            context["rejected_tasks"] = Task.objects.filter(
                customer=customer, status="rejected"
            )
            context["completed_tasks"] = Task.objects.filter(
                customer=customer, status="completed"
            )
            context["in_progress_tasks"] = Task.objects.filter(
                customer=customer, status="in-progress"
            )
        elif user.is_worker:
            worker = user.worker
            context["requested_tasks"] = Task.objects.filter(
                worker=worker, status="requested"
            )
            context["rejected_tasks"] = Task.objects.filter(
                worker=worker, status="rejected"
            )
            context["completed_tasks"] = Task.objects.filter(
                worker=worker, status="completed"
            )
            context["in_progress_tasks"] = Task.objects.filter(
                worker=worker, status="in-progress"
            )
        return context


@login_required
def task_accept(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.worker is not None:
        messages.warning(request, _("Task is already assigned to a worker."))
    else:
        task.worker = request.user.worker
        task.status = "in-progress"
        task.save()
        messages.success(request, _("Task accepted successfully."))
    return redirect("users:home")


@login_required
def task_reject(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.worker is not None:
        task.worker = None
        task.status = "requested"
        task.save()
        messages.success(request, _("Task rejected successfully."))
    else:
        messages.warning(request, _("Task is not assigned to any worker."))
    return redirect("users:home")


@login_required
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.worker is not None and task.worker == request.user.worker:
        task.status = "completed"
        task.save()
        messages.success(request, _("Task completed successfully."))
    else:
        messages.warning(request, _("Task is not assigned to you."))
    return redirect("users:home")


@login_required
def task_rate(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.status == "completed" and task.customer.user == request.user:
        if request.method == "POST":
            rating = request.POST.get("rating")
            review = request.POST.get("review")
            task.rating = rating
            task.review = review
            task.save()
            messages.success(request, _("Task rated successfully."))
            return redirect("users:home")
        elif task.rating is not None:
            return render(request, "tasks/task_rating.html", {"task": task})
        else:
            return render(request, "tasks/task_rate.html", {"task": task})
    else:
        messages.warning(request, _("Task is not completed or not assigned to you."))
        return redirect("users:home")

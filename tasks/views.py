from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib.auth.models import Group
from .models import Task
from .forms import TaskCreateForm
from users.models import Worker


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "tasks/task_create.html"

    def form_valid(self, form):
        task = form.save(commit=False)
        task.customer = self.request.user.customer
        task.worker = Worker.objects.get(pk=self.kwargs["pk"])
        task.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("users:home")


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "tasks/task_update.html"
    success_url = reverse_lazy("users:home")

    def form_valid(self, form):
        task = form.save(commit=False)
        task.save()
        messages.success(self.request, _("Task updated successfully."))
        return super().form_valid(form)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        if self.request.user.groups.filter(name="Customer").exists():
            customer = self.request.user.customer
            tasks = Task.objects.filter(customer=customer).order_by("-created_time")
            return tasks
        elif self.request.user.groups.filter(name="Worker").exists():
            worker = self.request.user.worker
            tasks = Task.objects.filter(worker=worker).order_by("-created_time")
            return tasks
        else:
            return Task.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.groups.filter(name="Customer").exists():
            customer = self.request.user.customer
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
        elif self.request.user.groups.filter(name="Worker").exists():
            worker = self.request.user.worker
            context["in_progress_tasks"] = Task.objects.filter(
                worker=worker, status="in-progress"
            )
            context["completed_tasks"] = Task.objects.filter(
                worker=worker, status="completed"
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
    if (
        task.worker is not None
        and task.worker == request.user.worker
        and task.status == "completed"
    ):
        if request.method == "POST":
            rating = request.POST.get("rating")
            review = request.POST.get("review")
            task.rating = rating
            task.review = review
            task.save()
            messages.success(request, _("Task rated successfully."))
            return redirect("users:home")
        else:
            return render(request, "tasks/task_rate.html", {"task": task})
    else:
        messages.warning(request, _("Task is not completed or not assigned to you."))
        return redirect("users:home")

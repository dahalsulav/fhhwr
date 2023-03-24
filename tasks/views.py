from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, FormView

from tasks.forms import (
    TaskCreateForm,
    TaskRequestCreateForm,
    TaskRequestUpdateForm,
    TaskUpdateForm,
    WorkerSearchForm,
)
from tasks.models import Task, TaskRequest
from users.models import Worker


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "tasks/task_create.html"
    success_url = reverse_lazy("tasks:task_list")

    def form_valid(self, form):
        form.instance.customer = self.request.user.customer
        return super().form_valid(form)


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        customer = self.request.user.customer
        return Task.objects.filter(
            Q(customer=customer) | Q(worker__customer=customer)
        ).order_by("-created_time")


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskUpdateForm
    template_name = "tasks/task_update.html"
    success_url = reverse_lazy("tasks:task_list")


class TaskRequestCreateView(LoginRequiredMixin, CreateView):
    model = TaskRequest
    form_class = TaskRequestCreateForm
    template_name = "tasks/task_request_create.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["task"] = self.kwargs["task_id"]
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["worker"] = self.request.user.worker
        return kwargs

    def form_valid(self, form):
        task_request = form.save(commit=False)
        task_request.requester = self.request.user.worker
        task_request.status = "pending"
        task_request.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Task request created successfully.")
        return reverse_lazy("tasks:task_detail", kwargs={"pk": self.kwargs["task_id"]})


class TaskRequestListView(LoginRequiredMixin, ListView):
    model = TaskRequest
    template_name = "tasks/taskrequest_list.html"
    context_object_name = "task_requests"

    def get_queryset(self):
        customer = self.request.user.customer
        return TaskRequest.objects.filter(
            task__customer=customer, status="requested"
        ).order_by("-requested_time")


class TaskRequestUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TaskRequest
    form_class = TaskRequestUpdateForm
    template_name = "tasks/taskrequest_update.html"

    def test_func(self):
        """Check if the user is a worker and the task request is assigned to them"""
        task_request = self.get_object()
        return task_request.worker == self.request.user.worker

    def form_valid(self, form):
        """Save the updated task request status"""
        task_request = form.save(commit=False)
        task_request.updated_time = datetime.now()  # update the last updated time
        task_request.save()
        messages.success(self.request, "Task request updated successfully")
        return redirect("tasks:taskrequest-list")


class WorkerSearchResultsView(LoginRequiredMixin, FormView, ListView):
    login_url = "users:login"  # Change this to the URL of your login page
    template_name = "users/worker_search_results.html"
    form_class = WorkerSearchForm
    context_object_name = "workers"

    def get_queryset(self):
        query = self.request.GET.get("query")
        if query:
            search_words = query.split()
            workers = Worker.objects.filter(
                Q(skills__name__icontains=search_words[0]), is_available=True
            )
            for word in search_words[1:]:
                workers |= Worker.objects.filter(Q(skills__name__icontains=word))
            print("Workers:", workers)
            return workers
        else:
            return Worker.objects.none()

    def form_valid(self, form):
        context = self.get_context_data()
        context["workers"] = self.get_queryset()
        return self.render_to_response(context)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

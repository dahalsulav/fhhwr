from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib import messages
from .forms import (
    CustomerRegistrationForm,
    WorkerRegistrationForm,
    CustomerUpdateForm,
    WorkerUpdateForm,
)
from .models import User, Customer, Worker, HourlyRateApproval
from .tokens import account_activation_token
from django.http import HttpResponseRedirect
from tasks.models import Task
from django.contrib.auth.decorators import login_required
from tasks.forms import TaskCreateForm


def base_view(request):
    workers = Worker.objects.filter(is_available=True)
    return render(request, "users/home.html", {"workers": workers})


class CustomerRegistrationView(CreateView):
    model = User
    form_class = CustomerRegistrationForm
    template_name = "users/customer_registration.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        response = super().form_valid(form)

        # Send email to the customer with the activation link
        mail_subject = "Activate your account"
        message = render_to_string(
            "users/activation_email.txt",
            {
                "user": self.object,
                "domain": self.request.META["HTTP_HOST"],
                "uid": urlsafe_base64_encode(force_bytes(self.object.pk)),
                "token": default_token_generator.make_token(self.object),
            },
        )
        to_email = form.cleaned_data.get("email")
        send_mail(
            mail_subject,
            message,
            settings.EMAIL_HOST_USER,
            [to_email],
            fail_silently=False,
        )

        # Optionally, send notification email to admin (not implemented)

        messages.success(
            self.request,
            "Please confirm your email address to complete the registration.",
        )
        return response


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerUpdateForm
    template_name = "users/customer_update.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return self.request.user.customer

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"instance": self.get_object()})
        return kwargs


class WorkerRegistrationView(CreateView):
    model = User
    form_class = WorkerRegistrationForm
    template_name = "users/worker_registration.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        response = super().form_valid(form)

        # Send email to the worker with the activation link
        mail_subject = "Activate your account"
        message = render_to_string(
            "users/activation_email.txt",
            {
                "user": self.object,
                "domain": self.request.META["HTTP_HOST"],
                "uid": urlsafe_base64_encode(force_bytes(self.object.pk)),
                "token": default_token_generator.make_token(self.object),
            },
        )
        to_email = form.cleaned_data.get("email")
        send_mail(
            mail_subject,
            message,
            settings.EMAIL_HOST_USER,
            [to_email],
            fail_silently=False,
        )

        messages.success(
            self.request,
            "Please confirm your email address to complete the registration.",
        )
        return response


class WorkerUpdateView(LoginRequiredMixin, UpdateView):
    model = Worker
    form_class = WorkerUpdateForm
    template_name = "users/worker_update.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return self.request.user.worker

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"instance": self.get_object()})
        return kwargs


class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def get_success_url(self):
        return reverse_lazy("users:home")

    def form_valid(self, form):
        username = self.request.POST["username"]
        password = self.request.POST["password"]
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        print("Login form is invalid.")
        print(form.errors)
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("users:home")


class ActivateAccountView(View):
    def get(self, request, *args, **kwargs):
        uidb64 = kwargs["uidb64"]
        token = kwargs["token"]
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.customer.email_verified = True
            user.is_active = True
            user.customer.save()
            user.save()
            messages.success(request, "Your account has been activated successfully.")
            return redirect("users:login")
        else:
            messages.error(request, "Invalid activation link.")
            return redirect("users:login")


class ActivateWorkerView(View):
    def get(self, request, *args, **kwargs):
        uidb64 = kwargs["uidb64"]
        token = kwargs["token"]
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            worker = Worker.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Worker.DoesNotExist):
            worker = None

        if worker is not None and default_token_generator.check_token(
            worker.user, token
        ):
            worker.email_verified = True
            worker.user.is_active = True
            worker.save()
            worker.user.save()
            messages.success(request, "Worker account has been activated successfully.")
            return redirect("users:login")
        else:
            messages.error(request, "Invalid activation link.")
            return redirect("users:login")


class UserProfileView(LoginRequiredMixin, DetailView):
    template_name = "users/user_profile.html"

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_customer:
            context["customer"] = user.customer
        elif user.is_worker:
            context["worker"] = user.worker
        return context


class WorkerSearchResultsView(View):
    def get(self, request):
        query = request.GET.get("query")
        workers = Worker.objects.all()
        if query:
            search_words = query.split()
            workers = workers.filter(skills__icontains=search_words[0])
            for word in search_words[1:]:
                workers = workers.filter(skills__icontains=word)
        context = {"workers": workers}
        return render(request, "users/worker_search_results.html", context)


class WorkerProfileView(LoginRequiredMixin, DetailView):
    model = Worker
    template_name = "users/worker_profile.html"

    def get_object(self):
        pk = self.kwargs.get("pk")
        return get_object_or_404(Worker, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        worker = self.get_object()

        if self.request.method == "POST":
            form = TaskCreateForm(worker, self.request.POST)
            if form.is_valid():
                task = form.save(commit=False)
                task.worker = worker
                task.customer = self.request.user.customer
                task.save()
                messages.success(self.request, _("Task created successfully."))
                return redirect("users:dashboard")
        else:
            form = TaskCreateForm(worker)

        context["worker"] = worker
        context["form"] = form
        return context


@login_required
def requested_tasks(request):
    tasks = Task.objects.filter(customer=request.user.customer, status="requested")
    return render(request, "users/requested_tasks.html", {"tasks": tasks})


@login_required
def in_progress_tasks(request):
    tasks = Task.objects.filter(worker=request.user.worker, status="in-progress")
    return render(request, "users/in_progress_tasks.html", {"tasks": tasks})


@login_required
def completed_tasks(request):
    tasks = Task.objects.filter(worker=request.user.worker, status="completed")
    return render(request, "users/completed_tasks.html", {"tasks": tasks})


@login_required
def rejected_tasks(request):
    tasks = Task.objects.filter(worker=request.user.worker, status="rejected")
    return render(request, "users/rejected_tasks.html", {"tasks": tasks})

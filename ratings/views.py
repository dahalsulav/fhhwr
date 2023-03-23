from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from ratings.forms import RatingCreateForm, RatingUpdateForm
from ratings.models import Rating


class RatingCreateView(LoginRequiredMixin, CreateView):
    model = Rating
    form_class = RatingCreateForm
    template_name = "ratings/rating_create.html"
    success_url = reverse_lazy("tasks:task_list")

    def form_valid(self, form):
        form.instance.customer = self.request.user.customer
        form.instance.task_request_id = self.kwargs["pk"]
        return super().form_valid(form)


class RatingUpdateView(LoginRequiredMixin, UpdateView):
    model = Rating
    form_class = RatingUpdateForm
    template_name = "ratings/rating_update.html"
    success_url = reverse_lazy("tasks:task_list")

    def get_object(self):
        rating = get_object_or_404(Rating, pk=self.kwargs["pk"])
        if rating.customer != self.request.user.customer:
            raise PermissionDenied("You cannot update this rating.")
        return rating

    def form_valid(self, form):
        form.instance.customer = self.request.user.customer
        return super().form_valid(form)

    def form_invalid(self, form):
        return redirect("tasks:task_list")

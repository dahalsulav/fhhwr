from django import forms
from django.core.exceptions import ValidationError

from ratings.models import Rating


class RatingCreateForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5, "step": 1}),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rating"].label = "Rating (1-5)"
        self.fields["comment"].label = "Comment"

    def clean(self):
        cleaned_data = super().clean()
        task_request = self.instance.task_request
        if not task_request.is_completed:
            raise ValidationError(
                "You can only provide a rating for a completed task request."
            )
        if task_request.worker.user == self.instance.customer.user:
            raise ValidationError("You cannot rate your own task request.")


class RatingUpdateForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5, "step": 1}),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rating"].label = "Rating (1-5)"
        self.fields["comment"].label = "Comment"

    def clean(self):
        cleaned_data = super().clean()
        task_request = self.instance.task_request
        if not task_request.is_completed:
            raise ValidationError(
                "You can only update a rating for a completed task request."
            )
        if task_request.worker.user == self.instance.customer.user:
            raise ValidationError("You cannot rate your own task request.")

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from tasks.models import TaskRequest
from users.models import Customer, Worker

RATING_CHOICES = [
    (1, "1 - Poor"),
    (2, "2 - Fair"),
    (3, "3 - Good"),
    (4, "4 - Very good"),
    (5, "5 - Excellent"),
]


class Rating(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="ratings"
    )
    task_request = models.ForeignKey(
        TaskRequest, on_delete=models.CASCADE, related_name="ratings"
    )
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="ratings")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=RATING_CHOICES,
    )
    comment = models.TextField(blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("customer", "task_request")

    def __str__(self):
        return f"{self.customer.user.username} rated {self.worker.user.username} {self.rating} stars"

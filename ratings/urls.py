from django.urls import path
from .views import RatingCreateView

app_name = "ratings"

urlpatterns = [
    path("create/<int:pk>/", RatingCreateView.as_view(), name="rating_create"),
]

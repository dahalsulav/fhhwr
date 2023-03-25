from django.urls import path

from tasks.views import (
    TaskCreateView,
    TaskDetailView,
    TaskListView,
    TaskRequestCreateView,
    TaskRequestListView,
    TaskRequestUpdateView,
    TaskUpdateView,
)

app_name = "tasks"

urlpatterns = [
    path("", TaskListView.as_view(), name="task_list"),
    path("create/", TaskCreateView.as_view(), name="task_create"),
    path("<int:pk>/", TaskDetailView.as_view(), name="task_detail"),
    path("<int:pk>/update/", TaskUpdateView.as_view(), name="task_update"),
    path(
        "<int:pk>/taskrequest/create/",
        TaskRequestCreateView.as_view(),
        name="taskrequest_create",
    ),
    path("taskrequests/", TaskRequestListView.as_view(), name="taskrequest-list"),
    path(
        "taskrequests/<int:pk>/update/",
        TaskRequestUpdateView.as_view(),
        name="taskrequest-update",
    ),
]

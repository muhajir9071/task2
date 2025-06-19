from django.urls import path
from .views import (
    ProjectListCreate, ProjectDetail,
    TaskListCreate, TaskDetail,
    TaskFilterView, ProjectSummary
)

urlpatterns = [
    # Project APIs
    path('projects/', ProjectListCreate.as_view()),
    path('projects/<str:pk>/', ProjectDetail.as_view()),
    path('projects/<str:project_id>/summary/', ProjectSummary.as_view()),

    # Task APIs (nested)
    path('projects/<str:project_id>/tasks/', TaskListCreate.as_view()),
    path('projects/<str:project_id>/tasks/<str:task_id>/', TaskDetail.as_view()),

    # Task Filters
    path('tasks/', TaskFilterView.as_view()),
]


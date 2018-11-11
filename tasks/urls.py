from django.contrib import admin
from django.urls import path
from tasks.views import TaskCreate,TaskList,TaskDetail

urlpatterns = [
    path('list/',TaskList.as_view()),
    path('create/',TaskCreate.as_view()),
    path('(\d+)/',TaskDetail.as_view())
]

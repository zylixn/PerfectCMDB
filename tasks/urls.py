from django.contrib import admin
from django.urls import path
from tasks.views import TaskCreate,TaskList,TaskDetail

urlpatterns = [
    path('list/',TaskList.as_view()),
    path('create/',TaskCreate.as_view()),
    path('detail/<pk>/',TaskDetail.as_view())
]

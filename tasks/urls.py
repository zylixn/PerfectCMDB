from django.contrib import admin
from django.conf.urls import url
from tasks.views import TaskCreate,TaskList,TaskDetail,test,TemplatesList

urlpatterns = [
    url('test/',test),
    url('templates/',TemplatesList.as_view()),
    url('list/',TaskList.as_view()),
    url('create/',TaskCreate.as_view()),
    url('detail/<pk>/',TaskDetail.as_view())
]

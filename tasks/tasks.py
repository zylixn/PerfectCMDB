# Create your tasks here
from celery import shared_task
from celery.task import Task,task
from PerfectCMDB.celery import app as celery_app

@shared_task
def mul(x, y):
    return x * y

@shared_task
def xsum(numbers):
    return sum(numbers)

@task(queue='server1')
def test_server1(server):
    return 'hello {0}'.format(server)

class DebugTask(Task):

    #queue = 'test_add'
    def __call__(self, *args, **kwargs):
        print('TASK STARTING: {0.name}[{0.request.id}]'.format(self))
        return super(DebugTask, self).__call__(*args, **kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('{0!r} failed: {1!r}'.format(task_id, exc))
        return super(DebugTask, self).on_failure(exc, task_id, args, kwargs, einfo)


@celery_app.task(base=DebugTask,name="tasks.add")
def add(x, y):
    return x + y

@celery_app.task(serializer='json')
def create_user(username, password):
    print("username: %s password: %s"%(username, password))
    return 'success'


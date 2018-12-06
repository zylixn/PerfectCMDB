# Create your tasks here
from celery import shared_task
from celery.task import Task,task
from PerfectCMDB.celery import app as celery_app
from celery.utils.log import get_task_logger
from tasks.bin import GetServerInfo
import json

logger = get_task_logger(__name__)

@shared_task
def mul(x, y):
    return x * y

@shared_task
def getserverinfo():
    result = dict()
    cpu_info = GetServerInfo.getcpuinfo()
    mem_info = GetServerInfo.getmemoryinfo()
    net_info = GetServerInfo.getnetworkinfo()
    result['cpu_info'] = cpu_info
    result['mem_info'] = mem_info
    result['net_info'] = net_info
    return json.dumps(result)

class DebugTask(Task):

    queue = 'test_add'
    def __call__(self, *args, **kwargs):
        print('TASK STARTING: {0.name}[{0.request.id}]'.format(self))
        return super(DebugTask, self).__call__(*args, **kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('{0!r} failed: {1!r}'.format(task_id, exc))
        return super(DebugTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        logger.info('Task {0} is finished'.format(task_id))
        return super(DebugTask, self).on_success(retval, task_id, args, kwargs)


@celery_app.task(base=DebugTask,name="PerfectCMDB.tasks.add",typing=False)
def add(x, y):
    logger.info('adding {0} + {1}'.format(x, y))
    return x + y

@celery_app.task(serializer='json')
def create_user(username, password):
    print("username: %s password: %s"%(username, password))
    return 'success'

@celery_app.task(bind=True)
def test_bind(self,x,y):
    logger.info('test_binding {0} + {1}'.format(x, y))
    return self.request.id



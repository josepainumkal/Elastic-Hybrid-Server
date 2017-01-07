from celery import Celery
import requests
import json
import ast
import docker
from redis import Redis

redis = Redis(host='workerdb', port=6379, db=0)
p = redis.pipeline()


taskId_startTime = {}
celery = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')


def plot_tsr(taskId, starttime, runtime, workername):
    plot_tsrfile = '/var/www/taskmanager'+'/c_task_start_runtime_wname.txt'
    with open(plot_tsrfile, "a") as infoFile:
        infoFile.write('{}\t{}\t{}\t{}\n'.format(taskId,starttime,runtime,workername))

def plot_twait(taskId, wait_time, runtime, workername):
    plot_tsrfile = '/var/www/taskmanager'+'/c_task_waittime.txt'
    with open(plot_tsrfile, "a") as infoFile:
        infoFile.write('{}\t{}\t{}\t{}\n'.format(taskId,round(wait_time,4),runtime,workername))

def plot_errorneous_tasks(taskId, workername, status):
    plot_errorfile = '/var/www/taskmanager'+'/c_erroneoustasks.txt'
    with open(plot_errorfile, "a") as infoFile:
        infoFile.write('{}\t{}\t{}\n'.format(taskId,workername,status))

def remove_model_run(modelrunId):
    deletemodel_url= 'http://192.168.99.101:5000/api/modelruns/'+str(modelrunId)
    r = requests.delete(url=deletemodel_url, headers=headers)

def remove_container(container_name):
    baseurl=redis.get(container_name)
    client = docker.Client(base_url=baseurl, tls=False)
    resp = client.remove_container(container=container_name, force='true',v='true')

    print "\nRemoved Container: ", container_name
    redis.delete(container_name)



def my_monitor():
    app = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')
    state = app.events.State()
    # p.set("tasks_completed", 0)
    # p.execute()

    # def announce_task_sent(event):
    #     state.event(event)
    #     task = state.tasks.get(event['uuid'])
    #     print task.hostname
    #     print('TASK CREATED: %s[%s] %s' % (task.name, task.uuid, task.info()))

    def announce_task_received(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])

        if task.hostname.startswith('celery@worker-'):
            celery.control.broadcast('shutdown', destination=[task.hostname])

        taskId_startTime[task.uuid] = task.timestamp 
        if task.hostname.startswith('celery@worker-'):
            celery.control.broadcast('shutdown', destination=[task.hostname])

    def announce_task_started(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])

        if task.hostname.startswith('celery@worker-'):
            celery.control.broadcast('shutdown', destination=[task.hostname])
   
        print "\nTask STARTED... ", task.uuid," : ",task.hostname 
        taskId_startTime[task.uuid] = task.timestamp 
        

    def announce_task_succeeded(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])

        # # storing completed job count in db
        # p.set("tasks_completed", int(redis.get('tasks_completed'))+1)
        # p.execute()

        if task.hostname.startswith('celery@worker-'):
            celery.control.broadcast('shutdown', destination=[task.hostname])
 
        print "\nTask FINISHED... ", task.uuid," : ",task.hostname 
        
        # modelId may not be present in allthe occassions
        # modelrun_id =  ast.literal_eval(task.info()['kwargs'])['modelrun_id']
        # remove_model_run(modelrun_id)
        
        try:
            container_name = task.hostname.split('@')[1]
            if container_name.startswith('worker-'):
                remove_container(container_name)
        except Exception, e:
            print "Exception Removing", container_name
        
        try:
            if task.uuid in taskId_startTime:
                starttime = taskId_startTime[task.uuid]
            else:
                starttime = task.timestamp-task.runtime
        except Exception, e:
            starttime = 0.0000000

        task_create_time =  redis.get(task.uuid)
        wait_time = starttime-float(task_create_time)

        # plot_tsr(taskId=task.uuid, starttime=starttime, runtime=task.runtime, workername=task.hostname)
        plot_twait(taskId=task.uuid, wait_time=wait_time, runtime=task.runtime, workername=task.hostname)
        redis.delete(task.uuid)




    def announce_task_failed(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])
   
        print "\nTask FAILED... ", task.uuid," : ",task.hostname 
        plot_errorneous_tasks(taskId=task.uuid, workername=task.hostname, status="FAILED")


    def announce_task_rejected(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])
   
        print "\nTask REJECTED... ", task.uuid," : ",task.hostname 
        plot_errorneous_tasks(taskId=task.uuid, workername=task.hostname, status="REJECTED")

    def announce_task_revoked(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])
   
        print "\nTask REVOCKED... ", task.uuid," : ",task.hostname 
        plot_errorneous_tasks(taskId=task.uuid, workername=task.hostname, status="REVOKED")


    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
                # 'task-sent': announce_task_sent, 
                'task-received': announce_task_received, 
                'task-started': announce_task_started, 
                'task-succeeded': announce_task_succeeded,  
                'task-revoked': announce_task_revoked,
                'task-rejected': announce_task_rejected,
                'task-failed':  announce_task_failed,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)

    
my_monitor()

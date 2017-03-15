from celery import Celery
import requests
import json
import ast
import docker
import os
from redis import Redis



###########################################################################################################################################################################################################################################

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDg5MTcyNzk5LCJuYmYiOjE0ODkxNzI3OTksImV4cCI6MTQ5MDAzNjc5OX0.0XyiYCTtywWFN1bCChpcmlYDSQqIrhur9CW2MAUx0mA'
model_api_url="http://192.168.99.101:5000/api/modelruns"
file_loc = '/var/www/taskmanager/app/main/generated_FILES/'

###########################################################################################################################################################################################################################################

def createFolderifNotExists(): 
    if not os.path.exists(file_loc):
        os.makedirs(file_loc)

createFolderifNotExists()

redis = Redis(host='workerdb', port=6379, db=0)
p = redis.pipeline()
redis1 = Redis(host='workerdb', port=6379, db=1)
p1 = redis1.pipeline()
redis3 = Redis(host='workerdb', port=6379, db=3)
p3 = redis3.pipeline()


taskId_startTime = {}
celery = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')


def plot_tsr(taskId, starttime, runtime, workername):
    # plot_tsrfile = '/var/www/taskmanager/app/main/'+'c_task_start_runtime_wname.txt'
    plot_tsrfile = file_loc+'c_task_start_runtime_wname.txt'
    with open(plot_tsrfile, "a") as infoFile:
        infoFile.write('{}\t{}\t{}\t{}\n'.format(taskId,starttime,runtime,workername))

def plot_twait(taskId, wait_time, runtime, workername, finishtime):
    
    plot_tsrfile = file_loc+'c_task_waittime.txt'
    # plot_tsrfile = '/var/www/taskmanager/app/main/generated_FILES/'+'c_task_waittime.txt'
    with open(plot_tsrfile, "a") as infoFile:
        infoFile.write('{}\t{}\t{}\t{}\t{}\n'.format(taskId,round(wait_time,4),runtime,workername,finishtime))

def plot_errorneous_tasks(taskId, workername, status):
    plot_tsrfile = file_loc+'c_erroneoustasks.txt'
    # plot_errorfile = '/var/www/taskmanager/app/main/'+'c_erroneoustasks.txt'
    with open(plot_errorfile, "a") as infoFile:
        infoFile.write('{}\t{}\t{}\n'.format(taskId,workername,status))


def remove_model_run(modelrunId, taskId):
    headers={'Content-Type':'application/json', 'Authorization': 'JWT %s' % token}
    deletemodel_url= model_api_url+'/'+str(modelrunId)
    r = requests.delete(url=deletemodel_url, headers=headers)
    print "Model Run REMOVED, ModelId: {}, taskId: {}".format(modelrunId,taskId)


def remove_container(container_name):
    baseurl=redis.get(container_name)
    client = docker.Client(base_url=baseurl, tls=False)
    resp = client.remove_container(container=container_name, force='true',v='true')

    print "\nRemoved Container: ", container_name
    redis.delete(container_name)



def my_monitor():
    app = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')
    state = app.events.State()

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
   
        print "\nTask STARTED_What?... ", task.uuid," : ",task.hostname 
        taskId_startTime[task.uuid] = task.timestamp 
        

    def announce_task_succeeded(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])

        # # storing completed job count in db
        # p.set("tasks_completed", int(redis.get('tasks_completed'))+1)
        # p.execute()

        if task.hostname.startswith('celery@worker-'):
            celery.control.broadcast('shutdown', destination=[task.hostname])
 
        print "\nTask FINISHEDu... ", task.uuid," : ",task.hostname 
        
        modelrun_id = redis1.get(task.uuid)
        remove_model_run(modelrun_id,task.uuid)

        try:
            container_name = task.hostname.split('@')[1]
            if container_name.startswith('worker-'):
                remove_container(container_name)
        except Exception, e:
            print "Exception Removing", container_name
        
        if task.uuid in taskId_startTime:
            starttime = taskId_startTime[task.uuid]
        else:
            starttime = task.timestamp-task.runtime
        
        try:
            task_create_time =  redis.get(task.uuid)
            wait_time = starttime-float(task_create_time)
        except Exception, e:
            print "Exception: Wait time is set to 0"
            wait_time = float(0.007)

        #defensive fix
        if wait_time<0:
            wait_time = wait_time * -1.0

        # plot_tsr(taskId=task.uuid, starttime=starttime, runtime=task.runtime, workername=task.hostname)
        plot_twait(taskId=task.uuid, wait_time=wait_time, runtime=task.runtime, workername=task.hostname, finishtime=task.timestamp)


        ####Storing required info in redis###################

        taskId = task.uuid
        modelId = modelrun_id
        wait_time=wait_time
        runtime=task.runtime
        workername=task.hostname

        if task.hostname.startswith('celery@worker-'):
            amount_remaining = float(redis3.get('budget_amount_remaning'))
            instance_rate_per_hr = float(redis3.get('instance_rate_per_hr'))
            amount_for_task = float((instance_rate_per_hr/3600)*runtime)
            amount_remaining = amount_remaining - amount_for_task
            p3.set('budget_amount_remaning', amount_remaining)
            p3.set('models_rented', int(redis3.get('models_rented'))+1)
            p3.execute()
            print "\t\t\tAmount remaining: ",amount_remaining
        else:
            amount_for_task = float(0)
            p3.set('models_owned', int(redis3.get('models_owned'))+1)
            p3.execute()


        task_str = str(taskId)+'|'+str(modelId)+'|'+str(round(wait_time,4))+'|'+str(round(runtime,4))+'|'+str(workername)+'|'+str(round(amount_for_task,4)) 
        newItem = []
        newItem.append(task_str)
        redis3.lpush('finished_task_list',*newItem)
        print "\t\t\tFinished Task Info: ",task_str
        ######################################################

        redis.delete(task.uuid)
        redis1.delete(task.uuid)
    



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

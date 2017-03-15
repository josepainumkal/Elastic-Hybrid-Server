import requests
import json
import ast
import docker
from redis import Redis
from celery import Celery

###########################################################################################################################################################################################################################################

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDg2NDEwMjAxLCJuYmYiOjE0ODY0MTAyMDEsImV4cCI6MTQ4NzI3NDIwMX0.K9HyjPcLgS3NxsWLUyP9sW6oJQU4I2rlA8qVWJE96tc'
model_api_url="http://134.197.42.21:5000/api/modelruns"

###########################################################################################################################################################################################################################################



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
        print "Task recieved"
      

    def announce_task_started(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])
   
        print "\nTask STARTED... ", task.uuid," : ",task.hostname 

    def announce_task_succeeded(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])
 
        print "\nTask FINISHED... ", task.uuid," : ",task.hostname," Run time:", task.runtime

        

    def announce_task_failed(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])
   
        print "\nTask FAILED... ", task.uuid," : ",task.hostname 
       

    def announce_task_rejected(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])
   
        print "\nTask REJECTED... ", task.uuid," : ",task.hostname 
       

    def announce_task_revoked(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])
   
        print "\nTask REVOCKED... ", task.uuid," : ",task.hostname 
       

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

import os 
import docker
import docker.utils

import requests
import json
from celery import Celery

from sets import Set
from time import sleep

# client = Client(base_url='unix://var/run/docker.sock')
client = docker.Client()
celery = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')

def create_worker_container(container_name):
    container_envs = docker.utils.parse_env_file('/var/www/taskmanager/container_env.txt')
    links=[('r-vw-dev_postgres-modeldb_1', 'modeldb'),('r-vw-dev_postgres-userdb_1', 'userdb'),('r-vw-dev_redis-workerdb_1', 'workerdb')]
    binds={"/vwstorage": "/vwstorage"}
    volumes = ['/vwstorage']

    volume_bindings = {
        '/vwstorage': {
            'bind': '/vwstorage',
            'mode': 'rw',
        },
    }

    host_config = client.create_host_config(
        binds=volume_bindings,
        links=links
        # port_bindings = port_bindings
    )

    container = client.create_container(
        # image='virtualwatershed/vwadaptor',
        image='josepainumkal/vwadaptor:jose_toolUI',
        environment=container_envs,
        stdin_open=True,
        tty=True,
        command='celery -A worker.modelworker worker --loglevel=info --autoreload --logfile=/celery.log -n '+ container_name,
        name=container_name,
        volumes=volumes,
        host_config=host_config,
        # networking_config = networking_config
        # host_config=create_host_config(port_bindings={2424:2425})
        # host_config=docker.utils.create_host_config(binds=binds)
    ) 
 
    response = client.start(container=container.get('Id'))
    print container.get('Id')

def remove_container(container):
    resp = client.remove_container(container=container, force='true',v='true')
    print resp

def queue_length():
    r = requests.get("http://192.168.99.100:5555/api/queues/length")
    # print r.status_code
    # print r.headers
    # print r.content

    resp_dict = json.loads(r.content)
    queue_length = int(resp_dict['active_queues'][0]['messages'])
    # print queue_length
    return queue_length


def worker_task_map_creator(worker_tasks_map):
    i = celery.control.inspect()

    celery_status = i.active()
    # print celery_status

    for key in celery_status.keys():
        # print key
        if(len(celery_status[key])!=0):    # if worker has any active job, then do the following
            if key in worker_tasks_map:   # # check worker present in worker_tasks map
                if (len(worker_tasks_map[key])>0):
                    worker_tasks_map[key].add(celery_status[key][0]['id'])
                else:
                    worker_tasks_map[key] = Set()
                    worker_tasks_map[key].add(celery_status[key][0]['id'])
            else:
                worker_tasks_map[key] = Set()
                worker_tasks_map[key].add(celery_status[key][0]['id'])

    # print worker_tasks_map
    return worker_tasks_map
    


def all_jobs_done():
    retval = True
    i = celery.control.inspect()
    for key in i.active().keys():
        if(len(i.active()[key])!=0):
            retval=False
            break
    return retval




# For all the newly created workers, the worker name will be starting as worker-1, worker-2,worker-3, etc.
#  save all newly created workers in a list. If i.active() returns {}, then remove the worker, after verifying it is a newly created worker


# Code for the selfmanaged worker system starts here. The idea is to first check the length of the queue,
# If queue length is not 0, that means the new job is in queue waiting for a worker. So we will spin up a new worker from scratch to handle the job.
# Once the job is done, the worker is destroyed. 

# list of newly created workers
print "\n ----Self Managed Worker System: STARTING -----"

worker_tasks_map = {}

worker_tasks_map = worker_task_map_creator(worker_tasks_map)
print "\nworker_tasks_map updated"
print worker_tasks_map
new_workers = []
worker_counter = 1



# execute below logic till no jobs are waiting in queue

while queue_length()>0:
    print "\nCurrent Queue Length is {}".format(queue_length())

    # spinup a new worker container
    container_name='worker-'+ str(worker_counter)
    print"\n Going to spin up a new worker Container {}".format(container_name)
    create_worker_container(container_name=container_name)
    new_workers.append(container_name)
    worker_counter=worker_counter+1
     
    print "\nSLEEP: Container Created..."
    sleep(3.5)  # sleep for 2.5 seconds. 

    worker_tasks_map = worker_task_map_creator(worker_tasks_map)
    print "\n worker_tasks_map updated..."
    print worker_tasks_map


print "\nCurrent Queue Length is {}".format(queue_length())," No job is on the Queue"


# Termination Logic
# check there is any worker existing with active job


exitCondion = False
while(exitCondion == False):
    print "\nEntered the exit condition loop"

    i = celery.control.inspect() 

    # what if new job comes in when all the workers are busy with active jobs
    while queue_length()>0:
        print "\nNEW JOBS IN THE QUEUE"
        print "\nCurrent Queue Length is {}".format(queue_length())
        # spinup a new worker container
        container_name='worker-'+ str(worker_counter)
        print"\n Going to spin up a new worker Container {}".format(container_name)
        create_worker_container(container_name=container_name)
        new_workers.append(container_name)
        worker_counter=worker_counter+1
         
        print "\nSLEEP: Container Created..."
        sleep(4)  # sleep for 2.5 seconds. 

        worker_tasks_map = worker_task_map_creator(worker_tasks_map)
        print "\nworker_tasks_map updated..."
        print worker_tasks_map


    
    exitCondion = True

    print "\nIterating over the active workers one by one"


    # celery_status = i.active()
    worker_tasks_map = worker_task_map_creator(worker_tasks_map)

    celery_status = i.active()
    for key in celery_status.keys():
        print "\nWorker being evaluated is {}".format(key)
        if(len(celery_status[key])!=0):
            jobId = celery_status[key][0]['id']
            exitCondion = False          #i.e. if exitCondition is False, then dont exit 
            print "\nWorker: {}".format(key)," Active Job: {}".format(jobId)        
            # print "\nWorker: {}".format(key),"ACTIVE JOB"         

        if (len(i.active()[key])==0):
            print "\nWorker: {}".format(key)," Jobs are FINISHED"        
            #This worker has finished the job. Remove the worker, if it is not the default worker
            worker_name = key.split('@')[1]
            if worker_name in new_workers:
                print "\nRemoving Worker: {}".format(key)      
                remove_container(container = worker_name)
                new_workers.remove(worker_name)
                print "\nREMOVED the worker container: {}".format(worker_name)      
                sleep(1)
                print "\nSLEEP: Container Removed..."


print "\nALL JOBS ARE FINISHED...HURRAY !!!"
print "\nThe worker Job map is ..."
print worker_tasks_map



             

   



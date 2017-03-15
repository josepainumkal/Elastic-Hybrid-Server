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
i = celery.control.inspect()


def create_worker_container(container_name):
    container_envs = docker.utils.parse_env_file('/var/www/taskmanager/container_env.txt')
    links=[('postgres-modeldb', 'modeldb'),('postgres-userdb', 'userdb'),('redis-workerdb', 'workerdb')]
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
        host_config=host_config
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


def get_job_status(jobId):
    url = 'http://192.168.99.100:5555/api/task/info/'+jobId
    r = requests.get(url)
    resp_dict = ''

    # print r.status_code
    # print r.headers
    # print r.content
    # print "RRRRRRRRRRR",r 
    try:
        resp_dict = json.loads(r.content)
        print "\tresp_dict SUCCESS [{}]".format(jobId)
    except Exception, e:
        print "\tr_except({}):".format(jobId), r
        print "\turl_except({}): ".format(jobId), url
    return resp_dict

    # state = resp_dict['state']
    # started_time = float(resp_dict['started'])
    # finished_time = float(resp_dict['succeeded'])
    # worker_name = resp_dict['worker']


def worker_task_map_creator(worker_tasks_map, celery_status):
   
    # celery_status = i.active()
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
# import time

# start_time = time.time()
# print "\n\n\n Start Time: ", start_time

# print "\n ----Self Managed Worker System: STARTING -----"

# worker_tasks_map = {}

# # worker_tasks_map = worker_task_map_creator(worker_tasks_map)
# # print "\nworker_tasks_map updated"
# # print worker_tasks_map
# new_workers = []
# worker_counter = 1



# # execute below logic till no jobs are waiting in queue

# # while queue_length()>0:
# #     print "\nCurrent Queue Length is {}".format(queue_length())

# #     # spinup a new worker container
# #     container_name='worker-'+ str(worker_counter)
# #     print"\n Going to spin up a new worker Container {}".format(container_name)
# #     create_worker_container(container_name=container_name)
# #     new_workers.append(container_name)
# #     worker_counter=worker_counter+1
     
# #     print "\nSLEEP: Container Created..."
# #     # sleep(2)  # sleep for 2.5 seconds. 

# #     # worker_tasks_map = worker_task_map_creator(worker_tasks_map)
# #     # print "\n worker_tasks_map updated..."
# #     # print worker_tasks_map


# # print "\nCurrent Queue Length is {}".format(queue_length())," No job is on the Queue"


# # Termination Logic
# # check there is any worker existing with active job


# exitCondion = False
# while(exitCondion == False):
#     # print "\nEntered the exit condition loop"

#     # i = celery.control.inspect() 

#     # what if new job comes in when all the workers are busy with active jobs
#     while queue_length()>0:
#         print "\nNEW JOBS IN THE QUEUE"
#         print "\nCurrent Queue Length is {}".format(queue_length())
#         # spinup a new worker container
#         container_name='worker-'+ str(worker_counter)
#         print"\n Going to spin up a new worker Container {}".format(container_name)
#         create_worker_container(container_name=container_name)
#         new_workers.append(container_name)
#         worker_counter=worker_counter+1
         
#         # print "\nSLEEP: Container Created..."
#         sleep(2)  # sleep for 2.5 seconds. 

#         # worker_tasks_map = worker_task_map_creator(worker_tasks_map)
#         # print "\nworker_tasks_map updated..."
#         # print worker_tasks_map


    
#     exitCondion = True

#     print "\nIterating over the active workers one by one"


#     # celery_status = i.active()
#     # worker_tasks_map = worker_task_map_creator(worker_tasks_map)

#     celery_status = i.active()
#     worker_tasks_map = worker_task_map_creator(worker_tasks_map, celery_status)
#     for key in celery_status.keys():
#         print "\nWorker being evaluated is {}".format(key)
#         if(len(celery_status[key])!=0):
#             jobId = celery_status[key][0]['id']
#             exitCondion = False          #i.e. if exitCondition is False, then dont exit 
#             print "\nWorker: {}".format(key)," Active Job: {}".format(jobId)        
#             # print "\nWorker: {}".format(key),"ACTIVE JOB"  


#         # celery_status = i.active()
#         if (len(celery_status[key])==0):
#             print "\nWorker: {}".format(key)," Jobs are FINISHED"        
#             #This worker has finished the job. Remove the worker, if it is not the default worker
#             worker_name = key.split('@')[1]
#             if worker_name in new_workers:
#                 print "\nRemoving Worker: {}".format(key)      
#                 remove_container(container = worker_name)
#                 new_workers.remove(worker_name)
#                 print "\nREMOVED the worker container: {}".format(worker_name)      
#                 # sleep(1)
#                 print "\nSLEEP: Container Removed..."
        

# # remove if any workers there
# print "new_workers", new_workers
# for l in new_workers:
#     remove_container(container = l)
#     new_workers.remove(l)
#     print "\nRemoved WWWorker: {}".format(l)   

# # celery_status = i.active()
# # if celery_status is not None:
# #         print cele
# #         print celery_status
# #         #     for l in new_workers:
# #         #         if ("celery@"+l) not in celery_status.keys():
# #         #             remove_container(container = l)
# #         #             new_workers.remove(l)
# #         #             print "\nREMOVEDDDDD the worker container: {}".format(l)     


# print "Start Time: ", start_time  
# end_time = time.time()
# print "Finished Time: ", end_time
# elapsed_time = end_time-start_time
# print "elaspsed time: ", elapsed_time


# print "\nALL JOBS ARE FINISHED...HURRAY !!!"
# print "\nThe worker Job map is ..."
# print worker_tasks_map

# ------------------------THE LOGIC STARTS HERE---------------------------------------------------------------------
def task_worker_map_(taskMap, celery_status):
   
    # celery_status = i.active()
    # print celery_status

    for key in celery_status.keys():

        if(len(celery_status[key])!= 0): 
            jobId = celery_status[key][0]['id']
            if jobId not in taskMap:
                taskMap[jobId] = key

    return taskMap


def exited_worker_containers():
    resp = client.containers(all=True, filters={'status':'exited'})
    # list of exited containers
    exited_worker_containers = []

    for d in resp:
        data = json.dumps(d) 
        # print data[0]
        nameofContainer = json.loads(data)['Names'][0]
        if nameofContainer.startswith('/worker-'):
            exited_worker_containers.append(nameofContainer.split('/')[1])
        
    return exited_worker_containers







# There are two set of workers - 1) rented workers and 2) non-rented workers.
import time
start_time = time.time()
print "\n\n\n Start Time: ", start_time
print "\n ----Self Managed Worker System: STARTING -----"
worker_tasks_map = {}
taskMap = {}
new_workers = set()
worker_counter = 1

while True:
    # check the queue length
    while queue_length()>0:
        print "\nNEW JOBS IN THE QUEUE. No free workers left. Lets spin up a new worker ?"
        print "\t\tCurrent Queue Length is {}".format(queue_length())
        # spinup a new worker container
        container_name='worker-'+ str(worker_counter)
        print"\t\tGoing to spin up a new worker container {}".format(container_name)

        # New worker has to wait for this much time to grab a job
        print "\t\tSLEEP: Self initiated sleep for rented worker started. Please wait!"
        sleep(5)

        create_worker_container(container_name=container_name)
        sleep(5)
        # new_workers.append(container_name)
        worker_counter = worker_counter+1

        # sleep for 2.5 seconds. time to pick job by the worker
        # worker_name = "celery@"+container_name
        # celery.control.broadcast('shutdown', destination=[worker_name])

        #  rented workers are assumed to do exactly one job. The worker should be removed after processing one job
        #celerey status will not show all the active jobs, beause i am shutting down containers.


    celery_status = i.active()
    if  celery_status is None:
        print "\n\ncelery_status is returned none. Retrying once again..."
        celery_status = i.active()

    # print "\nCELERY STATUS: ", celery_status
    # worker_tasks_map = worker_task_map_creator(worker_tasks_map, celery_status)
    if celery_status is not None:
        for key in celery_status.keys():
            if key.startswith('celery@worker-'):
                # shutdown new workers, otherwise they will grab other jobs
                new_workers.add(key)
                celery.control.broadcast('shutdown', destination=[key])
                # print '\n\n\n\n\n\n\n new_worker::',new_workers

            if(len(celery_status[key])!= 0): 
                jobId = celery_status[key][0]['id']
                if jobId not in taskMap:
                    taskMap[jobId] = key
    

    # taskMap = task_worker_map_(taskMap, celery_status)
    print "\nTASKMAP---: ", taskMap
    print "\nNew Workers---: ", new_workers,"\n"

    # code to shutdown new workers, otherwise they will grab other jobs.
    # for worker in new_workers:
    #     celery_worker_name = 'celery@'+worker
    #     celery.control.broadcast('shutdown', destination=[celery_worker_name])

    #defensive fix: removing worker containers that are already exited. Since we call shutdown above, the worker container will normally exit after job is processed 
    # container itself will exit?, because worker is the only process running on those container.So when worker process exit, container stops.
    workers_exited = exited_worker_containers()
    for worker in workers_exited:
        celery_worker = 'celery@'+worker
        try:
            exited_workers_jobId = taskMap.keys()[taskMap.values().index(celery_worker)] 
            taskMap.pop(exited_workers_jobId,0)  
        except ValueError, e:
            pass      
        # if worker in new_workers:
        remove_container(container=worker)
        new_workers.remove(celery_worker)
        print "\n REMOVED*** the worker container: {}".format(worker)   


    # iterate over jobids to see which all jobs are finished
    for jobId in taskMap.copy():
        resp = get_job_status(jobId)
        # print "resp", resp
        # print "resp['state']", resp['state']
        if resp != '' and resp['state'] == "SUCCESS":
            # remove worker for this jobid, if the worker is rented
            worker_name = taskMap[jobId]
            # worker_name = taskMap[jobId].split('@')[1]
            taskMap.pop(jobId,0)
            if worker_name in new_workers:
                # print "\nRemoving Worker: {}".format(worker_name)      
                new_workers.remove(worker_name)
                worker_name = worker_name.split('@')[1]
                remove_container(container = worker_name)

                print "\nREMOVED the worker container: {}".format(worker_name)      
                # sleep(1)
                print "\nSLEEP: Container Removed..."
            
   
   



    


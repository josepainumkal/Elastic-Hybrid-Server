import os 
import docker
import docker.utils
import requests
import json
import time

from celery import Celery
from time import sleep
from multiprocessing import Process, Value, Array, Manager
from celery.result import AsyncResult

# client = Client(base_url='unix://var/run/docker.sock')
client = docker.Client()
celery = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')
i = celery.control.inspect()

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDgyMzc4NzQxLCJuYmYiOjE0ODIzNzg3NDEsImV4cCI6MTQ4NDk3MDc0MX0.wN6S445-3mwNztsqwox7tspSPLn5J6fXQl12ERqFEs8'
payload = {'description': 'test_description', 'model_name': 'prms', 'title': 'test01'}
headers={'Content-Type':'application/json', 'Authorization': 'JWT %s' % token}
upload_headers={'Authorization': 'JWT %s' % token}
modelrun_headers={'Authorization': 'JWT %s' % token}
control_file_name = '1-month_input/LC.control'
data_file_name = '1-month_input/data.nc'
param_file_name = '1-month_input/parameter.nc'
controlfile = {'file': open(control_file_name, 'rb')}
datafile = {'file': open(data_file_name, 'rb')}
paramfile = {'file': open(param_file_name, 'rb')}

new_workers = set()
task_model_map = Manager().dict()
# taskMap = Manager().dict()
# modeltaskdetails = '/var/www/taskmanager'+'/modeltaskdetails.txt'
modelrunId_starttime = Manager().dict()
jobid_jobstart = {}



def create_model_run():
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDgxNjY3Mzc3LCJuYmYiOjE0ODE2NjczNzcsImV4cCI6MTQ4NDI1OTM3N30.UTUjBQu9s0RHK2xxDFGYRjwtOoRRb4boXUpxGsz6m1Q'
    payload = {'description': 'test_description', 'model_name': 'prms', 'title': 'test01'}
    headers={'Content-Type':'application/json', 'Authorization': 'JWT %s' % token}

    r = requests.post(url="http://192.168.99.100:5000/api/modelruns", json=payload, headers=headers)
    resp_dict = json.loads(r.content)
    modelrun_id = resp_dict['id']

    # print r.status_code, r.reason
    # print resp_dict['id']

    # File Upload
    payload = {'resource_type':'input'}
    upload_headers={'Authorization': 'JWT %s' % token}
    file_upload_url = 'http://192.168.99.100:5000/api/modelruns/'+str(modelrun_id)+'/upload'
    control_file_name = '1-month_input/LC.control'
    controlfile = {'file': open(control_file_name, 'rb')}
    data_file_name = '1-month_input/data.nc'
    datafile = {'file': open(data_file_name, 'rb')}
    param_file_name = '1-month_input/parameter.nc'
    paramfile = {'file': open(param_file_name, 'rb')}

    r = requests.post(url=file_upload_url, data={'resource_type':'control'}, headers=upload_headers, files=controlfile)
    #print r.status_code, r.reason  
    # print r.content
    r = requests.post(url=file_upload_url, data={'resource_type':'data'}, headers=upload_headers, files=datafile)
    # print r.status_code, r.reason  
    # print r.content
    r = requests.post(url=file_upload_url, data={'resource_type':'param'}, headers=upload_headers, files=paramfile)
    # print r.status_code, r.reason  
    # print r.content

    # run model
    modelrun_url = 'http://192.168.99.100:5000/api/modelruns/'+str(modelrun_id)+'/start'
    modelrun_headers={'Authorization': 'JWT %s' % token}
    r = requests.put(url=modelrun_url, headers=modelrun_headers)
    resp_dict = json.loads(r.content)
    task_id = resp_dict['modelrun']['task_id']
    # print r.status_code, r.reason  
    # print r.content

    # with open(modeltaskdetails, "a") as infoFile:
    #     infoFile.write('{}\t{}\n'.format(task_id, modelrun_id))

    if r.status_code == 200:
        print "---Modelrun Created------Modelrun Id: {0}-------Task Id: {1}".format(modelrun_id, task_id)
        
        task_model_map[task_id]=modelrun_id
        modelrunId_starttime[modelrun_id] =  time.time()

    else:
        print "Model run creation resulted in an error. Please rectify the error and proceed..."


# def create_model_run():
#     r = requests.post(url="http://192.168.99.100:5000/api/modelruns", json=payload, headers=headers)
#     resp_dict = json.loads(r.content)
#     modelrun_id = resp_dict['id']

#     file_upload_url = 'http://192.168.99.100:5000/api/modelruns/'+str(modelrun_id)+'/upload'
#     r = requests.post(url=file_upload_url, data={'resource_type':'control'}, headers=upload_headers, files=controlfile)
#     r = requests.post(url=file_upload_url, data={'resource_type':'data'}, headers=upload_headers, files=datafile)
#     r = requests.post(url=file_upload_url, data={'resource_type':'param'}, headers=upload_headers, files=paramfile)

#     modelrun_url = 'http://192.168.99.100:5000/api/modelruns/'+str(modelrun_id)+'/start'
#     r = requests.put(url=modelrun_url, headers=modelrun_headers)
#     task_id = resp_dict['modelrun']['task_id']
    
#     if r.status_code == 200:
#         print "---Modelrun Created------Modelrun Id: {0}-------Task Id: {1}".format(modelrun_id, task_id)
#         task_model_map[task_id]=modelrun_id
#     else:
#         print "Model run creation resulted in an error. Please rectify the error and proceed..."


def poisson_job_generator():
    while True:
        create_model_run()
        sleep(10)


def remove_model_run(modelrunId):
    deletemodel_url= 'http://192.168.99.100:5000/api/modelruns/'+str(modelrunId)
    r = requests.delete(url=deletemodel_url, headers=headers)
    print "---REMOVED model run------Modelrun Id: {0}".format(modelrunId)

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

# def total_rented_workers():
#     return len(new_workers)


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
        # print "\tresp_dict SUCCESS [{}]".format(jobId)
    except Exception, e:
        pass
        # print "\tr_except({}):".format(jobId), r
        # print "\turl_except({}): ".format(jobId), url
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


def total_rented_worker_containers():
    resp = client.containers()
    active_worker_containers = []
    for d in resp:
        data = json.dumps(d) 
        # print data[0]
        nameofContainer = json.loads(data)['Names'][0]
        if nameofContainer.startswith('/worker-'):
            active_worker_containers.append(nameofContainer.split('/')[1])
        
    return len(active_worker_containers)



def serve_job_queue():
    worker_counter = 1
    while True:
        # print "Total Rented Workers: ", len(taskMap)
        while queue_length()>0 and total_rented_worker_containers()<2:
            print "\nNEW JOBS IN THE QUEUE. No free workers left. Lets spin up a new worker ?"
            print "\t\tCurrent Queue Length is {}".format(queue_length())
            # spinup a new worker container
            container_name='worker-'+ str(worker_counter)
            print"\t\tGoing to spin up a new worker container {}".format(container_name)

            # New worker has to wait for this much time to grab a job
            print "\t\tSLEEP: Self initiated sleep for rented worker started. Please wait!"
            sleep(5)

            create_worker_container(container_name=container_name)
            sleep(10)
            # new_workers.append(container_name)
            worker_counter = worker_counter+1

# def exceptionedtasks(modelId,jobId,jobcreatetime,workername):
#     modeltaskdetails = '/var/www/taskmanager'+'/exceptionedtasks.txt'
#     with open(modeltaskdetails, "a") as infoFile:
#         infoFile.write('{}\t{}\t{}\t{}\n'.format(modelId,jobId,jobcreatetime,workername))

def exceptionedtasks(modelId,jobId,jobcreatetime,jobstarttime,jobsucceededtime,jobruntime,workername):
    modeltaskdetails = '/var/www/taskmanager'+'/exceptionedtasks.txt'
    with open(modeltaskdetails, "a") as infoFile:
        infoFile.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(modelId,jobId,jobcreatetime,jobstarttime,jobsucceededtime,jobruntime,workername))

def store_to_file(modelId,jobId,jobcreatetime,jobstarttime,jobsucceededtime,jobruntime,workername):
    modeltaskdetails = '/var/www/taskmanager'+'/modeltaskdetails.txt'
    modelidList = []
    try:
        with open(modeltaskdetails, "r") as infoFile:
            for line in infoFile:
                values=line.split('\t')
                modelidList.append([0])
            if modelId not in modelidList:
                with open(modeltaskdetails, "a") as infoFile:
                    infoFile.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(modelId,jobId,jobcreatetime,jobstarttime,jobsucceededtime,jobruntime,workername))
    except Exception,e:
        with open(modeltaskdetails, "w") as infoFile:
            infoFile.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(modelId,jobId,jobcreatetime,jobstarttime,jobsucceededtime,jobruntime,workername))



   



# def remove_exited_workers():
#     while True:
#         workers_exited = exited_worker_containers()
#         for worker in workers_exited:
#             celery_worker = 'celery@'+worker
#             try:
#                 exited_workers_jobId = taskMap.keys()[taskMap.values().index(celery_worker)] 
#                 taskMap.pop(exited_workers_jobId,0)  
#                 if exited_workers_jobId in task_model_map:
#                     del_modelrunId = task_model_map[exited_workers_jobId]
#                     remove_model_run(del_modelrunId)
#                     print "\n REMOVED the model run details"
#             except ValueError, e:
#                 pass      
#              # if worker in new_workers:
#             remove_container(container=worker)
#             new_workers.remove(celery_worker)
#             print "\n REMOVED*** the worker container: {}".format(worker)   

# There are two set of workers - 1) rented workers and 2) non-rented workers.
start_time = time.time()
print "\n\n\n Start Time: ", start_time
print "\n ----Self Managed Worker System: STARTING -----"
worker_tasks_map = {}
taskMap = {}
worker_counter = 1

mg_process = Process(target=poisson_job_generator)
mg_process.start()

sq_process = Process(target=serve_job_queue)
sq_process.start()

# rw_process = Process(target=remove_exited_workers)
# rw_process.start()




while True:
    # check the queue length
    # while queue_length()>0:
    #     print "\nNEW JOBS IN THE QUEUE. No free workers left. Lets spin up a new worker ?"
    #     print "\t\tCurrent Queue Length is {}".format(queue_length())
    #     # spinup a new worker container
    #     container_name='worker-'+ str(worker_counter)
    #     print"\t\tGoing to spin up a new worker container {}".format(container_name)

    #     # New worker has to wait for this much time to grab a job
    #     print "\t\tSLEEP: Self initiated sleep for rented worker started. Please wait!"
    #     sleep(5)

    #     create_worker_container(container_name=container_name)
    #     sleep(5)
    #     # new_workers.append(container_name)
    #     worker_counter = worker_counter+1

        # sleep for 2.5 seconds. time to pick job by the worker
        # worker_name = "celery@"+container_name
        # celery.control.broadcast('shutdown', destination=[worker_name])

        #  rented workers are assumed to do exactly one job. The worker should be removed after processing one job
        #celerey status will not show all the active jobs, beause i am shutting down containers.

   

    celery_status = i.active()
    print "celery_status: ",celery_status
    while celery_status is None:
        print "\n\ncelery_status is returned none. Retrying once again..."
        sleep(1)
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
                    jobid_jobstart[jobId] = time.time()

            # else:
            #     if key.startswith('celery@worker-'):
            #         new_workers.remove(key)
            #         celery.control.broadcast('shutdown', destination=[key])
            #         remove_container(container=key.split('@')[1])
            #         print "\n REMOVED*** the worker container: {}".format(key.split('@')[1])   


    

    # taskMap = task_worker_map_(taskMap, celery_status)
    print "\nTASKMAP----: ", taskMap
    print "New Workers  : ", new_workers
    print "Queue Length :", queue_length()
    print "Total Rented Workers :", total_rented_worker_containers()
    print "task model map :", task_model_map,"\n"

    

    # code to shutdown new workers, otherwise they will grab other jobs.
    # for worker in new_workers:
    #     celery_worker_name = 'celery@'+worker
    #     celery.control.broadcast('shutdown', destination=[celery_worker_name])

    #defensive fix: removing worker containers that are already exited. Since we call shutdown above, the worker container will normally exit after job is processed 
    # container itself will exit?, because worker is the only process running on those container.So when worker process exit, container stops.
    # workers_exited = exited_worker_containers()
    # for worker in workers_exited:
    #     celery_worker = 'celery@'+worker
    #     try:
    #         exited_workers_jobId = taskMap.keys()[taskMap.values().index(celery_worker)] 

    #         print "\n task_model_map: ", task_model_map
    #         resp = get_job_status(exited_workers_jobId)
    #         if resp != '':
    #             succeededtime = float(resp['succeeded'])
    #             runtime = float(resp['runtime'])
    #             starttime = succeededtime - runtime
    #             modelstarttime = modelrunId_starttime[task_model_map[exited_workers_jobId]]
    #             store_to_file(modelId=task_model_map[exited_workers_jobId ],jobId=exited_workers_jobId ,jobcreatetime=modelstarttime,jobstarttime=starttime,jobruntime=runtime,jobsucceededtime=succeededtime, workername=celery_worker)
    #         else:
    #             exceptionedtasks(modelId=task_model_map[exited_workers_jobId ],jobId=exited_workers_jobId ,jobcreatetime=modelrunId_starttime[task_model_map[exited_workers_jobId ]],workername=celery_worker)

    #         taskMap.pop(exited_workers_jobId,0)  

    #         if exited_workers_jobId in task_model_map:
    #             del_modelrunId = task_model_map[exited_workers_jobId]
    #             remove_model_run(del_modelrunId)
    #             print "\n REMOVED the model run details"

    #     except ValueError, e:
    #         pass      
    #     # if worker in new_workers:
    #     remove_container(container=worker)
    #     new_workers.remove(celery_worker)
    #     print "\n REMOVED*** the worker container: {}".format(worker)   


   # iterate over jobids to see which all jobs are finished
    for jobId in taskMap.copy():
        if AsyncResult(jobId).state == 'SUCCESS':
            worker_name = taskMap[jobId]
            taskMap.pop(jobId,0)
            if jobId in task_model_map:
                remove_model_run(task_model_map[jobId])
                print "\n REMOVED the model run details"
            if worker_name in new_workers:
                new_workers.remove(worker_name)
                worker_name = worker_name.split('@')[1]
                remove_container(container = worker_name)
                print "\nREMOVED the worker container: {}".format(worker_name),"\n"
            
            sleep(5)
            resp = get_job_status(jobId)
            print 'resp:',resp
            if resp != '':
                succeededtime = float(resp['succeeded'])
                runtime = float(resp['runtime'])
                starttime = succeededtime - runtime
                print 'task_model_map:', task_model_map
                modelstarttime = modelrunId_starttime[task_model_map[jobId]]
                store_to_file(modelId=task_model_map[jobId],jobId=jobId,jobcreatetime=modelstarttime,jobstarttime=starttime,jobruntime=runtime,jobsucceededtime=succeededtime, workername=worker_name)
            else:
                modelstarttime = modelrunId_starttime[task_model_map[jobId]]
                succeededtime = time.time()
                runtime = succeededtime - jobid_jobstart[jobId]
                exceptionedtasks(modelId=task_model_map[jobId],jobId=jobId,jobcreatetime=modelstarttime,jobstarttime=jobid_jobstart[jobId],jobruntime=runtime,jobsucceededtime=succeededtime,workername=worker_name)



    workers_exited = exited_worker_containers()
    for worker in workers_exited:
        remove_container(container=worker)
        celery_worker = 'celery@'+worker
        new_workers.remove(celery_worker)
        print "\n REMOVED*** the worker container: {}".format(worker)   







   


    # # iterate over jobids to see which all jobs are finished
    # for jobId in taskMap.copy():
    #     resp = get_job_status(jobId)
    #     # print "resp", resp
    #     # print "resp['state']", resp['state']
    #     if resp != '' and resp['state'] == "SUCCESS":
    #         # remove worker for this jobid, if the worker is rented
    #         worker_name = taskMap[jobId]
    #         # worker_name = taskMap[jobId].split('@')[1]
    #         # taskMap.pop(jobId,0)
    #         if jobId in task_model_map:
    #             del_modelrunId = task_model_map[jobId]
    #             remove_model_run(del_modelrunId)
    #             print "\n REMOVED the model run details"

    #         if worker_name in new_workers:
    #             # print "\nRemoving Worker: {}".format(worker_name)      
    #             new_workers.remove(worker_name)
    #             worker_name = worker_name.split('@')[1]
    #             remove_container(container = worker_name)

    #             print "\nREMOVED the worker container: {}".format(worker_name)      
    #             # sleep(1)
    #             print "\nSLEEP: Container Removed..."

    #         print "\n task_model_map: ", task_model_map
    #         succeededtime = float(resp['succeeded'])
    #         runtime = float(resp['runtime'])
    #         starttime = succeededtime - runtime
    #         modelstarttime = modelrunId_starttime[task_model_map[jobId]]
    #         store_to_file(modelId=task_model_map[jobId],jobId=jobId,jobcreatetime=modelstarttime,jobstarttime=starttime,jobruntime=runtime,jobsucceededtime=succeededtime, workername=taskMap[jobId])
    #         taskMap.pop(jobId,0)

            
   
   



    


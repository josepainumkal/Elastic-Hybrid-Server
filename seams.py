from __future__ import division
import os 
import docker
import docker.utils
import requests
import json
import time
import random

from celery import Celery
from time import sleep
from multiprocessing import Process, Value, Array, Manager
from celery.result import AsyncResult

from redis import Redis
redis = Redis(host='workerdb', port=6379, db=0)

# client = Client(base_url='unix://var/run/docker.sock')
# client = docker.Client()
celery = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')
i = celery.control.inspect()

# token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDgyMzc4NzQxLCJuYmYiOjE0ODIzNzg3NDEsImV4cCI6MTQ4NDk3MDc0MX0.wN6S445-3mwNztsqwox7tspSPLn5J6fXQl12ERqFEs8'
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDgyODcwMTExLCJuYmYiOjE0ODI4NzAxMTEsImV4cCI6MTQ4NTQ2MjExMX0.fq7F6oroRe0IkUrl2LBw1k7prtxgCoX9lHjB_Mwmrn4'
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

# new_workers = set()
task_model_map = Manager().dict()
taskMap = Manager().dict()
new_workers = Manager().list()

# modeltaskdetails = '/var/www/taskmanager'+'/modeltaskdetails.txt'
modelrunId_starttime = Manager().dict()
# jobid_jobstart = {}
jobid_jobstart = Manager().dict()


params_seams = Manager().dict()
time_interval = 0
total_rented_modelruns_allowed=0

total_money = float(100)
container_rate_per_min = float(1)
tavg_modelrun_secs = float(8.35)
tavg_modelrun_mins = float(tavg_modelrun_secs/60)
total_rented_modelruns_allowed = int(total_money/(tavg_modelrun_mins*container_rate_per_min))
# time interval calculated for one hour. i.e, we are distributing total_rented_modelruns_allowed among the one hour
time_interval = float(60.0/total_rented_modelruns_allowed)
time_interval=time_interval*60

print '\nTotal Money: ', total_money, '$'
print 'Rate of Container: ', container_rate_per_min,' $/min'
print 'Average time for modelrun : ', tavg_modelrun_secs,' sec'
print 'Maximum rented modelruns  : ', total_rented_modelruns_allowed
print 'Calculated time interval  : ', time_interval,' sec'

p = redis.pipeline()
p.set('MaxRentedModelsAllowed', total_rented_modelruns_allowed)
p.set('CurrentRentedModels', 0)
p.execute()

workerName_hostip = Manager().dict()
rented_hostips = Manager().list()
rented_hostips.append('http://10.0.9.14:2375')
rented_hostips.append('http://10.0.9.15:2375')
rented_hostips.append('http://10.0.9.16:2375')

rentedHostMachines =  Manager().dict()
rentedHostCredentials_1=['docker','tcuser'] 
rentedHostMachines['192.168.99.102'] = rentedHostCredentials_1
rentedHostCredentials_2=['docker','tcuser'] 
rentedHostMachines['192.168.99.103'] = rentedHostCredentials_2
rentedHostCredentials_3=['docker','tcuser'] 
rentedHostMachines['192.168.99.104'] = rentedHostCredentials_3



#for statistics...remove after use
completedjobs = Manager().list()

def rsync_modelfiles():
    for ip in rentedHostMachines.copy():
        credentials = rentedHostMachines[ip]
        uname = credentials[0]
        pwd = credentials[1]
        addr = 'sshpass -p '+'"'+pwd+'"'+' rsync -a -e "ssh" --rsync-path="sudo rsync" /vwstorage/ '+uname+'@'+ip+':/vwstorage/'
        os.system(addr)
        # os.system('sshpass -p "tcuser" rsync -a -e "ssh" --rsync-path="sudo rsync" /vwstorage/ docker@192.168.99.102:/vwstorage/')


    

def plot_completedjobs_time():
    while True:
        plot_completedjobs_time = '/var/www/taskmanager'+'/completedjobs_time.txt'
        with open(plot_completedjobs_time, "a") as infoFile:
            infoFile.write('{}\t\t{}\t\t{}\n'.format(time.time(),len(completedjobs), queue_length()))
        sleep(2)
    


def plot_qlength_time():
    plot_qlength_time = '/var/www/taskmanager'+'/ql_time.txt'
    time.time()

    with open(plot_qlength_time, "a") as infoFile:
        infoFile.write('{}\t\t{}\n'.format(time.time(),queue_length()))



def create_model_run():
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDgyOTkwNjkxLCJuYmYiOjE0ODI5OTA2OTEsImV4cCI6MTQ4NTU4MjY5MX0.Z7dfiT9o2oMT_fQzRvddrolwmG98r0TAJKcvwOD90IE'
    payload = {'description': 'test_description', 'model_name': 'prms', 'title': 'test01'}
    headers={'Content-Type':'application/json', 'Authorization': 'JWT %s' % token}

    r = requests.post(url="http://192.168.99.101:5000/api/modelruns", json=payload, headers=headers)
    resp_dict = json.loads(r.content)
    modelrun_id = resp_dict['id']

    # print r.status_code, r.reason
    # print resp_dict['id']

    # File Upload
    payload = {'resource_type':'input'}
    upload_headers={'Authorization': 'JWT %s' % token}
    file_upload_url = 'http://192.168.99.101:5000/api/modelruns/'+str(modelrun_id)+'/upload'
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
    rsync_modelfiles()

    # run model
    modelrun_url = 'http://192.168.99.101:5000/api/modelruns/'+str(modelrun_id)+'/start'
    modelrun_headers={'Authorization': 'JWT %s' % token}
    r = requests.put(url=modelrun_url, headers=modelrun_headers)
    resp_dict = json.loads(r.content)
    task_id = resp_dict['modelrun']['task_id']
    # print r.status_code, r.reason  
    # print r.content

    if r.status_code == 200:
        print "\nModelrun Created.  Modelrun Id: {0}.  Task Id: {1}".format(modelrun_id, task_id)
        
        task_model_map[task_id]=modelrun_id
        modelrunId_starttime[modelrun_id] =  time.time()

    else:
        print "\nModel run creation resulted in an error. Please rectify the error and proceed..."



def remove_model_run(modelrunId):
    deletemodel_url= 'http://192.168.99.101:5000/api/modelruns/'+str(modelrunId)
    r = requests.delete(url=deletemodel_url, headers=headers)
    rsync_modelfiles()
    # print "---REMOVED model run------Modelrun Id: {0}".format(modelrunId)

def create_worker_container(container_name):
    baseurl= rented_hostips.pop(0)
    rented_hostips.append(baseurl)
    client = docker.Client(base_url=baseurl, tls=False)

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
        links=links,
        network_mode='my-net'
        # port_bindings = port_bindings
    )

    networking_config = client.create_networking_config({
        'my-net': client.create_endpoint_config(
            ipv4_address='10.0.9.0/24',
            # aliases=['foo', 'bar'],
            links=links
        )
    })

    container = client.create_container(
        image='josepainumkal/vwadaptor:jose_toolUI',
        environment=container_envs,
        stdin_open=True,
        tty=True,
        # command='celery -A worker.modelworker worker -Q rentedQueue --loglevel=info --autoreload --logfile=/celery.log -n '+ container_name,
        command='celery -A worker.modelworker worker --loglevel=info --autoreload --logfile=/celery.log -n '+ container_name,
        name=container_name,
        volumes=volumes,
        host_config=host_config,
        networking_config = networking_config
        # host_config=create_host_config(port_bindings={2424:2425})
        # host_config=docker.utils.create_host_config(binds=binds)
    ) 
 
    response = client.start(container=container.get('Id'))
    workerName_hostip[container_name] = baseurl


def remove_container(container):
    if container.startswith('worker-'):
        baseurl = workerName_hostip[container]
        client = docker.Client(base_url=baseurl, tls=False)
    else:
        client = docker.Client()

    resp = client.remove_container(container=container, force='true',v='true')
    # print resp

def queue_length():
    r = requests.get("http://192.168.99.101:5555/api/queues/length")
    # print r.status_code, r.headers, r.content
    resp_dict = json.loads(r.content)
    queue_length = int(resp_dict['active_queues'][0]['messages'])
    # print queue_length
    return queue_length

# def total_rented_workers():
#     return len(new_workers)


def get_job_status(jobId):
    url = 'http://192.168.99.101:5555/api/task/info/'+jobId
    r = requests.get(url)
    resp_dict = ''
    # print r.status_code

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


# ------------------------THE LOGIC STARTS HERE--------------------------------------------------------------------



def exited_worker_containers():
    exited_worker_containers = []
    for ip in rented_hostips:
        baseurl= ip
        client = docker.Client(base_url=baseurl, tls=False)
        resp = client.containers(all=True, filters={'status':'exited'})
        for d in resp:
            data = json.dumps(d) 
            # print data[0]
            nameofContainer = json.loads(data)['Names'][0]
            if nameofContainer.startswith('/worker-'):
                exited_worker_containers.append(nameofContainer.split('/')[1])

    # list of exited containers
    return exited_worker_containers


def total_rented_worker_containers():
    active_worker_containers = []
    for ip in rented_hostips:
        baseurl= ip
        client = docker.Client(base_url=baseurl, tls=False)
        resp = client.containers()
        for d in resp:
            data = json.dumps(d) 
            # print data[0]
            nameofContainer = json.loads(data)['Names'][0]
            if nameofContainer.startswith('/worker-'):
                active_worker_containers.append(nameofContainer.split('/')[1])
        
    return len(active_worker_containers)


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


def poisson_job_generator():
    # rateParameter = 1.0/float(60.0/18) # 20 is lambda
    while True:
        create_model_run()
        sleep(1)
        # sleep(random.expovariate(rateParameter))

# def rented_queue_length():
#     return redis.llen('rentedQueue')


def containerCreationSnippet(worker_counter):
    container_name='worker-'+ str(worker_counter)
    print "\nNew container spinned... ", container_name
    create_worker_container(container_name=container_name)
    worker_counter = worker_counter+1
    new_celery_worker = 'celery@'+container_name
    
    celery_status = celery.control.inspect().active()
    while celery_status is None:
        # print "\n\ncelery_status is returned none. Retrying once again..."
        celery_status = celery.control.inspect().active()

    while new_celery_worker not in celery_status.keys():
        # print new_celery_worker,'not in celery_status. So Retrying'
        celery_status = celery.control.inspect().active()

    while (len(celery_status[new_celery_worker]) == 0):
        # print "\n The new worker {} has not grabbed a job. Retrying...".format(new_celery_worker)
        celery_status = celery.control.inspect().active()

    jobId = celery_status[new_celery_worker][0]['id']
    taskMap[jobId] = new_celery_worker
    jobid_jobstart[jobId] = time.time()
    celery.control.broadcast('shutdown', destination=[new_celery_worker])
    new_workers.append(new_celery_worker)

    currentRentedModels = int(redis.get('CurrentRentedModels'))
    currentRentedModels=currentRentedModels+1
    p = redis.pipeline()
    p.set('CurrentRentedModels', currentRentedModels)
    p.execute()

    print "\nTask Map Updated, shutdow initiated for {}".format(new_celery_worker)    
    print "TASKMAP----: ", taskMap
    print "New Workers  : ", new_workers
    print "Queue Length :", queue_length()
    print "Total Rented Workers :", total_rented_worker_containers()
    print "MaxRentedModelsAllowed :", total_rented_modelruns_allowed
    print "CurrentRentedModels :", currentRentedModels

    return worker_counter


def rentedContainerCreation():
    wastedChances = 0
    worker_counter = 1 
    maxRentedModelsAllowed = int(redis.get('MaxRentedModelsAllowed'))
    currentRentedModels = int(redis.get('CurrentRentedModels'))

    while (currentRentedModels<maxRentedModelsAllowed):
        if queue_length()>0:
            worker_counter = containerCreationSnippet(worker_counter)

            while wastedChances>0:
                 if queue_length()>0:
                    worker_counter = containerCreationSnippet(worker_counter)
                    wastedChances = wastedChances-1

        else:
            wastedChances = wastedChances+1
            # print "wastedChances :", wastedChances


        sleep(time_interval)

        currentRentedModels = int(redis.get('CurrentRentedModels'))
        print "wastedChances-now :", wastedChances


      
  
# def serve_job_queue():
#     worker_counter = 1
#     while True:
#         while queue_length()>0 :
#             print "\nNEW JOBS IN THE QUEUE. No free workers left. Lets spin up a new worker ?"
#             # spinup a new worker container
#             container_name='worker-'+ str(worker_counter)
#             print"\t\tGoing to spin up a new worker container {}".format(container_name)

#             # New worker has to wait for this much time to grab a job
#             print "\t\tSLEEP({} seconds): Self initiated sleep for rented worker started. Please wait!".format(time_interval)
#             sleep(time_interval)

#             create_worker_container(container_name=container_name)
#             # sleep(10)
#             # new_workers.append(container_name)
#             worker_counter = worker_counter+1

#             celery_status = celery.control.inspect().active()
#             new_celery_worker = 'celery@'+container_name
            

#             while celery_status is None:
#                 print "\n\ncelery_status is returned none. Retrying once again..."
#                 sleep(1)
#                 celery_status = celery.control.inspect().active()

#             while new_celery_worker not in celery_status.keys():
#                 print new_celery_worker,'not in celery_status. So Retrying'
#                 celery_status = celery.control.inspect().active()

#             while (len(celery_status[new_celery_worker]) == 0):
#                 print "\n The new worker {} has not grabbed a job. Retrying...".format(new_celery_worker)
#                 celery_status = celery.control.inspect().active()
               

        
#             jobId = celery_status[new_celery_worker][0]['id']
#             taskMap[jobId] = new_celery_worker
#             jobid_jobstart[jobId] = time.time()
#             celery.control.broadcast('shutdown', destination=[new_celery_worker])
#             new_workers.append(new_celery_worker)

#             print "\nTask Map Updated, shutdow initiated for {}".format(new_celery_worker)    
#             print "TASKMAP----: ", taskMap
#             print "New Workers  : ", new_workers
#             print "Queue Length :", queue_length()
#             print "Rented Queue Length :", rented_queue_length()
#             print "Total Rented Workers :", total_rented_worker_containers()
#             print "MaxRentedModelsAllowed :", total_rented_modelruns_allowed
#             print "CurrentRentedModels :", int(redis.get('CurrentRentedModels'))




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
# taskMap = {}

print "\n ******* Self Managed Worker System: Stared *******"
# moneydetails()

plot_process = Process(target=plot_completedjobs_time)
plot_process.start()

sq_process = Process(target=rentedContainerCreation)
sq_process.start()
mg_process = Process(target=poisson_job_generator)
mg_process.start()
# rw_process = Process(target=remove_exited_workers)
# rw_process.start()

while True:
    celery_status = celery.control.inspect().active()
    while celery_status is None:
        print "\ncelery status is None***. Retrying..."
        # sleep(1)
        celery_status = celery.control.inspect().active()

    for key in celery_status.keys():
         if(len(celery_status[key])!= 0): 
            jobId = celery_status[key][0]['id']
            if jobId not in taskMap:
                taskMap[jobId] = key
                jobid_jobstart[jobId] = time.time()

                print "\nTask Map Updated, Added new job id, {}".format(jobId)    
                print "TASKMAP----: ", taskMap
                print "New Workers  : ", new_workers
                print "Queue Length :", queue_length()
                print "Total Rented Workers :", total_rented_worker_containers()
                # print "Rented Queue Length :", rented_queue_length()
                print "MaxRentedModelsAllowed :", int(redis.get('MaxRentedModelsAllowed'))
                print "CurrentRentedModels :", int(redis.get('CurrentRentedModels'))
                plot_qlength_time()




    # iterate over jobids to see which all jobs are finished
    for jobId in taskMap.copy():
        if AsyncResult(jobId).state == 'SUCCESS':
            ctime = time.time()
            worker_name = taskMap[jobId]
            taskMap.pop(jobId,0)

            completedjobs.append(jobId)

            print "\nTask Map Updated, Task Finished: {}".format(jobId)
            # print "TASKMAP----: ", taskMap
            # print "New Workers  : ", new_workers
            # print "Queue Length :", queue_length()
            # print "Total Rented Workers :", total_rented_worker_containers()

            if jobId in task_model_map:
                remove_model_run(task_model_map[jobId])
                print "Removed the MODEL RUN({}) details".format(task_model_map[jobId])
            if worker_name in new_workers:
                new_workers.remove(worker_name)
                worker_name = worker_name.split('@')[1]
                remove_container(container = worker_name)
                print "Removed the WORKER container: {}".format(worker_name),"\n"
            
            # sleep(1)
            resp = get_job_status(jobId)
            # print 'resp:',resp
            if resp != '':
                succeededtime = float(resp['succeeded'])
                runtime = float(resp['runtime'])
                starttime = succeededtime - runtime
                # print 'task_model_map:', task_model_map
                modelstarttime = modelrunId_starttime[task_model_map[jobId]]
                store_to_file(modelId=task_model_map[jobId],jobId=jobId,jobcreatetime=modelstarttime,jobstarttime=starttime,jobruntime=runtime,jobsucceededtime=succeededtime, workername=worker_name)
            else:
                modelstarttime = modelrunId_starttime[task_model_map[jobId]]
                succeededtime=ctime
                runtime = succeededtime - jobid_jobstart[jobId]
                exceptionedtasks(modelId=task_model_map[jobId],jobId=jobId,jobcreatetime=modelstarttime,jobstarttime=jobid_jobstart[jobId],jobruntime=runtime,jobsucceededtime=succeededtime,workername=worker_name)

            

    workers_exited = exited_worker_containers()
    for worker in workers_exited:
        print "\nExited Worker Container detected. Worker: {}".format(worker)
        remove_container(container=worker)
        celery_worker = 'celery@'+worker
        new_workers.remove(celery_worker)
        print "Removed the WORKER container: {}".format(worker)






































# while True:
#     pass
#     # check the queue length
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

   

    # celery_status = i.active()
    # # print "celery_status: ",celery_status
    # while celery_status is None:
    #     print "\n\ncelery_status is returned none. Retrying once again..."
    #     sleep(1)
    #     celery_status = i.active()


    # # print "\nCELERY STATUS: ", celery_status
    # # worker_tasks_map = worker_task_map_creator(worker_tasks_map, celery_status)
    # if celery_status is not None:
    #     for key in celery_status.keys():
    #         if key.startswith('celery@worker-'):
    #             # shutdown new workers, otherwise they will grab other jobs
    #             new_workers.add(key)
    #             # celery.control.broadcast('shutdown', destination=[key])
    #             # print '\n\n\n\n\n\n\n new_worker::',new_workers

    #         if(len(celery_status[key])!= 0): 
    #             jobId = celery_status[key][0]['id']
    #             if jobId not in taskMap:
    #                 taskMap[jobId] = key
    #                 jobid_jobstart[jobId] = time.time()

            # else:
            #     if key.startswith('celery@worker-'):
            #         new_workers.remove(key)
            #         celery.control.broadcast('shutdown', destination=[key])
            #         remove_container(container=key.split('@')[1])
            #         print "\n REMOVED*** the worker container: {}".format(key.split('@')[1])   


    

    # taskMap = task_worker_map_(taskMap, celery_status)
    # print "\nTASKMAP----: ", taskMap
    # print "New Workers  : ", new_workers
    # print "Queue Length :", queue_length()
    # print "Total Rented Workers :", total_rented_worker_containers()
    # print "task model map :", task_model_map,"\n"

    

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
    # for jobId in taskMap.copy():
    #     if AsyncResult(jobId).state == 'SUCCESS':
    #         worker_name = taskMap[jobId]
    #         taskMap.pop(jobId,0)
    #         if jobId in task_model_map:
    #             remove_model_run(task_model_map[jobId])
    #             print "\n REMOVED the model run details"
    #         if worker_name in new_workers:
    #             new_workers.remove(worker_name)
    #             worker_name = worker_name.split('@')[1]
    #             remove_container(container = worker_name)
    #             print "\nREMOVED the worker container: {}".format(worker_name),"\n"
            
    #         sleep(5)
    #         resp = get_job_status(jobId)
    #         print 'resp:',resp
    #         if resp != '':
    #             succeededtime = float(resp['succeeded'])
    #             runtime = float(resp['runtime'])
    #             starttime = succeededtime - runtime
    #             print 'task_model_map:', task_model_map
    #             modelstarttime = modelrunId_starttime[task_model_map[jobId]]
    #             store_to_file(modelId=task_model_map[jobId],jobId=jobId,jobcreatetime=modelstarttime,jobstarttime=starttime,jobruntime=runtime,jobsucceededtime=succeededtime, workername=worker_name)
    #         else:
    #             modelstarttime = modelrunId_starttime[task_model_map[jobId]]
    #             succeededtime = time.time()
    #             runtime = succeededtime - jobid_jobstart[jobId]
    #             exceptionedtasks(modelId=task_model_map[jobId],jobId=jobId,jobcreatetime=modelstarttime,jobstarttime=jobid_jobstart[jobId],jobruntime=runtime,jobsucceededtime=succeededtime,workername=worker_name)



    # workers_exited = exited_worker_containers()
    # for worker in workers_exited:
    #     remove_container(container=worker)
    #     celery_worker = 'celery@'+worker
    #     new_workers.remove(celery_worker)
    #     print "\n REMOVED*** the worker container: {}".format(worker)   







   


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

            
   
   



    


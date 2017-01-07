from __future__ import division
import os 
import docker
import docker.utils
import requests
import json
import time
import random

import sys
import random
import datetime
import thread


from celery import Celery
from time import sleep
from multiprocessing import Process, Value, Array, Manager
from celery.result import AsyncResult

from redis import Redis
redis = Redis(host='workerdb', port=6379, db=0)
p = redis.pipeline()

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


total_money = float(3.0)
container_rate_per_min = float(1.0)
tavg_modelrun_secs = float(4)
tavg_modelrun_mins = float(tavg_modelrun_secs/60)
total_rented_modelruns_allowed = int(total_money/(tavg_modelrun_mins*container_rate_per_min))
# time interval calculated for one hour. i.e, we are distributing total_rented_modelruns_allowed among the one hour
time_interval = float(120.0/total_rented_modelruns_allowed)
# time_interval=time_interval*60
# time_interval=0

time_interval = time_interval
# time_interval=0

print '\nTotal Money: ', total_money, '$'
print 'Rate of Container: ', container_rate_per_min,' $/min'
print 'Average time for modelrun : ', tavg_modelrun_secs,' sec'
print 'Maximum rented modelruns  : ', total_rented_modelruns_allowed
print 'Calculated time interval  : ', time_interval,' sec'
print 'Total Models Allowed ', total_rented_modelruns_allowed 


workerName_hostip = Manager().dict()
rented_hostips = Manager().list()
rented_hostips.append('http://10.0.9.9:2375')
rented_hostips.append('http://10.0.9.10:2375')
rented_hostips.append('http://10.0.9.12:2375')

rentedHostMachines =  Manager().dict()
rentedHostCredentials_1=['docker','tcuser'] 
rentedHostMachines['192.168.99.102'] = rentedHostCredentials_1
rentedHostCredentials_2=['docker','tcuser'] 
rentedHostMachines['192.168.99.103'] = rentedHostCredentials_2
rentedHostCredentials_3=['docker','tcuser'] 
rentedHostMachines['192.168.99.104'] = rentedHostCredentials_3



completedjobs = Manager().list()

def rsync_modelfiles():

    for ip in rentedHostMachines.copy():
        credentials = rentedHostMachines[ip]
        uname = credentials[0]
        pwd = credentials[1]
        addr = 'sshpass -p '+'"'+pwd+'"'+' rsync -a -e "ssh" --rsync-path="sudo rsync" /vwstorage/ '+uname+'@'+ip+':/vwstorage/'
        os.system(addr)
        # os.system('sshpass -p "tcuser" rsync -a -e "ssh" --rsync-path="sudo rsync" /vwstorage/ docker@192.168.99.102:/vwstorage/') 

def plot_tc(taskId, createtime):
    plot_tcfile = '/var/www/taskmanager'+'/c_task_createtime.txt'
    with open(plot_tcfile, "a") as infoFile:
        infoFile.write('{}\t{}\n'.format(taskId,createtime))

def plot_completedjobs_time():
    while True:
        plot_completedjobs_time = '/var/www/taskmanager'+'/c_finished_qlength.txt'
        with open(plot_completedjobs_time, "a") as infoFile:
            infoFile.write('{}\t\t{}\t\t{}\n'.format(time.time(),len(completedjobs), queue_length()))
        sleep(2)
# def plot_finishedCount_qlen():
#     plot_finishedCount = '/var/www/taskmanager'+'/c_finished_qlength.txt'
#     with open(plot_finishedCount, "a") as infoFile:
#         infoFile.write('{}\t\t{}\t\t{}\n'.format(time.time(),redis.get('tasks_completed'), queue_length()))



def create_model_run():
    start = time.time()

    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDgzNzMzNDA3LCJuYmYiOjE0ODM3MzM0MDcsImV4cCI6MTQ4NDU5NzQwN30.9LKx_ttRrfQPD0gMoDQTd037-QkPKpWz6X_g5Fl4LXg'
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
        p.set(task_id, time.time())
        p.execute()
        
        print "\nModelrun Created.  Modelrun Id: {0}.  Task Id: {1}".format(modelrun_id, task_id)
        
        task_model_map[task_id]=modelrun_id
        taskMap[task_id]=modelrun_id
        modelrunId_starttime[modelrun_id] =  time.time()
        plot_tc(task_id, time.time())

    else:
        print "\nModel run creation resulted in an error. Please rectify the error and proceed..."

    end=time.time()
    duration = end-start
    return duration


def remove_model_run(modelrunId):
    deletemodel_url= 'http://192.168.99.101:5000/api/modelruns/'+str(modelrunId)
    r = requests.delete(url=deletemodel_url, headers=headers)
    rsync_modelfiles()
    # print "---REMOVED model run------Modelrun Id: {0}".format(modelrunId)

def create_worker_container(container_name):
    start = time.time()

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
        command='celery -A worker.modelworker worker -c 1 --loglevel=info --autoreload --logfile=/celery.log -n '+ container_name,
        name=container_name,
        volumes=volumes,
        host_config=host_config,
        networking_config = networking_config
        # host_config=create_host_config(port_bindings={2424:2425})
        # host_config=docker.utils.create_host_config(binds=binds)
    ) 
 
    response = client.start(container=container.get('Id'))
    workerName_hostip[container_name] = baseurl

    # storing worker_name and baseurl in redisdb
    p.set(container_name, baseurl)
    p.execute()

    end = time.time()
    duration = end-start
    return duration  

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
    resp_dict = json.loads(r.content)
    queue_length = int(resp_dict['active_queues'][0]['messages'])
    return queue_length


def get_job_status(jobId):
    url = 'http://192.168.99.101:5555/api/task/info/'+jobId
    r = requests.get(url)
    resp_dict = ''

    try:
        resp_dict = json.loads(r.content)
        # state = resp_dict['state']
        # started_time = float(resp_dict['started'])
        # print "\tresp_dict SUCCESS [{}]".format(jobId)
    except Exception, e:
        pass

    return resp_dict


# ------------------------THE LOGIC STARTS HERE--------------------------------------------------------------------

def exceptionedtasks(modelId,jobId,jobcreatetime,jobstarttime,jobsucceededtime,jobruntime,workername):
    modeltaskdetails = '/var/www/taskmanager'+'/c_exceptionedtasks.txt'
    with open(modeltaskdetails, "a") as infoFile:
        infoFile.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(modelId,jobId,jobcreatetime,jobstarttime,jobsucceededtime,jobruntime,workername))

def store_to_file(modelId,jobId,jobcreatetime,jobstarttime,jobsucceededtime,jobruntime,workername):
    modeltaskdetails = '/var/www/taskmanager'+'/c_modeltaskdetails.txt'
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

def plot_job_wait_time(modelId,jobId,jobcreatetime,jobstarttime):
    job_wait_details = '/var/www/taskmanager'+'/c_job_wait_details.txt'
    with open(job_wait_details, "a") as infoFile:
        job_wait_time = jobstarttime - jobcreatetime
        infoFile.write('{}\t{}\t{}\t{}\t{}\n'.format(modelId,jobId,jobcreatetime,jobstarttime,job_wait_time))

# def poisson_job_generator():
#     modelno=0
#     rateParameter = 1.0/float(120.0/70) # 20 is lambda
#     while True:
#         duration = create_model_run()
#         modelno=modelno+1
#         print"\nModel Created-------------------- : ",modelno
#         # sleep(1)
#         sl = random.expovariate(rateParameter)-duration
#         if sl<0:
#             sleep(0)
#         else:
#             sleep(sl)

        

def poisson_job_generator():

    max_min = 2.0
    input_lambda = 70
    modelno=0
    for i in range(input_lambda):
        create_model_run()
        print"\nModel Created-------------------- : ",i
        sleeping_time = max_min*60/input_lambda - 0.99760492222
        sleep(sleeping_time)
    # sys.exit()

    # '''
    # this function is used to generate models with possion distribution
    # max_min is maximum minute
    # '''
    # start_time = datetime.datetime.now()
    # current_time = datetime.datetime.now()
    # passing_min = 0.0
    # modelCount = 0
    # rateParameter = 1.0/float(float(max_min)*60/input_lambda) # 20 is lambda
    # while passing_min<=max_min and modelCount<input_lambda:
    #     current_time = datetime.datetime.now()
    #     passing_min = (current_time-start_time).total_seconds()/60
    #     print "create " + str(modelCount) + " model at:" + str(passing_min)
    #     create_model_run()
    #     modelno = modelno+1
    #     print"\n Model NO CREATED-------------------- : ",modelno
    #     sleep_time = random.expovariate(rateParameter)
    #     if sleep_time/60 + passing_min >= max_min:
    #         break
    #     else:
    #         time.sleep(sleep_time)
        
    #     modelCount = modelCount+1
    #     # print "/////////////-----------NO OF MODELS CREATED: ",modelCount
    # if modelCount == input_lambda:
    #         sys.exit()
    # else:
    #     for i in range(input_lambda - modelCount):
    #         print "create another model at:" + str(passing_min)
    #         create_model_run()
    #         modelno = modelno+1
    #         print"\n Model NO CREATED-------------------- : ",modelno
    #     sys.exit()

# poisson_job_generator(2,20)

# def rented_queue_length():
#     return redis.llen('rentedQueue')


def containerCreationSnippet(worker_counter):
    container_name='worker-'+ str(worker_counter)
    print "\nNew Container spinning..... ", container_name 
    duration = create_worker_container(container_name=container_name)
    worker_counter = worker_counter+1

    return worker_counter, duration


def rentedContainerCreation():
    wastedChances = 0
    worker_counter = 1 
    currentRentedModels = 0
    duration=0

    while (currentRentedModels<=total_rented_modelruns_allowed):
        if queue_length()>0:
            worker_counter, duration = containerCreationSnippet(worker_counter)
            currentRentedModels =currentRentedModels+1

            print "\nTotal Models Allowed ", total_rented_modelruns_allowed 
            print "Rented Models Count: ", currentRentedModels 

            while wastedChances>0 and currentRentedModels<=total_rented_modelruns_allowed:
                 if queue_length()>0:
                    worker_counter, duration = containerCreationSnippet(worker_counter)
                    currentRentedModels =currentRentedModels+1
                    wastedChances = wastedChances-1

        else:
            wastedChances = wastedChances+1
            print "wastedChances-now :", wastedChances

        sl = time_interval-duration
        if sl<0:
            sleep(0)
        else:
            sleep(sl)
 
        
# def remove_exited_worker_containers():
#   while True:
#       for ip in rented_hostips:
#           baseurl= ip
#           client = docker.Client(base_url=baseurl, tls=False)
#           resp = client.containers(all=True, filters={'status':'exited'})
#           for d in resp:
#               data = json.dumps(d) 
#               # print data[0]
#               nameofContainer = json.loads(data)['Names'][0]
#               if nameofContainer.startswith('/worker-'):
#                   container_name = nameofContainer.split('/')[1]
#                   remove_container(container=container_name)
#                   print "\nRemoved the WORKER container: {}".format(container_name)



print "\n ******* Self Managed Worker System: Started *******"

# sq_process = Process(target=rentedContainerCreation)
# sq_process.start()
# mg_process = Process(target=poisson_job_generator)
# mg_process.start()
# # rm_exited_workers = Process(target=remove_exited_worker_containers)
# # rm_exited_workers.start()
# plt_finished_qlen = Process(target=plot_completedjobs_time)
# plt_finished_qlen.start()

thread.start_new_thread(rentedContainerCreation,())
thread.start_new_thread(poisson_job_generator,())
thread.start_new_thread(plot_completedjobs_time,())



while True:
    # sleep(2)
    # plot_finishedCount_qlen()

    for jobId in taskMap.copy():
        if AsyncResult(jobId).state == 'SUCCESS':
            if jobId not in completedjobs:
                completedjobs.append(jobId)
                taskMap.pop(jobId,0)





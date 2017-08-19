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

task_model_map = Manager().dict()
taskMap = Manager().dict()
new_workers = Manager().list()
modelrunId_starttime = Manager().dict()
jobid_jobstart = Manager().dict()
workerName_hostip = Manager().dict()
rented_hostips = Manager().list()
completedjobs = Manager().list()
rentedHostMachines =  Manager().dict()

celery = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')
redis = Redis(host='workerdb', port=6379, db=0)
p = redis.pipeline()

redis1 = Redis(host='workerdb', port=6379, db=1)
p1 = redis1.pipeline()

redis3 = Redis(host='workerdb', port=6379, db=3)
p3 = redis3.pipeline()

########################################################################################################################################################################################################################################

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDg2ODQ3MDAyLCJuYmYiOjE0ODY4NDcwMDIsImV4cCI6MTQ4NzcxMTAwMn0.7TGFaJ7SaZuvsFb0YJPR1ef9YzvQ5i6pRcWgSxqnoRE'

model_api_url="http://192.168.99.101:5000/api/modelruns"
rented_hostips.append('http://10.0.9.10:2375')

rentedHostCredentials_1=['docker','tcuser'] 
rentedHostMachines['192.168.99.102'] = rentedHostCredentials_1

total_money = float(2.26)
container_rate_per_min = float(1.0)
tavg_modelrun_secs = float(3.4)
tavg_modelrun_mins = float(tavg_modelrun_secs/60)
total_rented_modelruns_allowed = int(total_money/(tavg_modelrun_mins*container_rate_per_min))
time_interval = float(360/total_rented_modelruns_allowed)

time_interval = time_interval-0.08

########################################################################################################################################################################################################################################
p3.set('budget_amount', total_money)
p3.set('budget_amount_remaning', total_money)
p3.set('container_rate_per_min', container_rate_per_min)
models_owned = 0
models_rented = 0
p3.set('models_owned', int(models_owned))
p3.set('models_rented', int(models_rented))
p3.execute()


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

def create_model_run():
    start = time.time()

    ###### Create Model Id
    payload = {'description': 'test_description', 'model_name': 'prms', 'title': 'test01'}
    headers={'Content-Type':'application/json', 'Authorization': 'JWT %s' % token}
    r = requests.post(url=model_api_url, json=payload, headers=headers)
    resp_dict = json.loads(r.content)
    modelrun_id = resp_dict['id']

    ###### File Upload
    payload = {'resource_type':'input'}
    upload_headers={'Authorization': 'JWT %s' % token}
    file_upload_url = model_api_url+'/'+str(modelrun_id)+'/upload'
    control_file_name = '1-month_input/LC.control'
    controlfile = {'file': open(control_file_name, 'rb')}
    data_file_name = '1-month_input/data.nc'
    datafile = {'file': open(data_file_name, 'rb')}
    param_file_name = '1-month_input/parameter.nc'
    paramfile = {'file': open(param_file_name, 'rb')}
    r = requests.post(url=file_upload_url, data={'resource_type':'control'}, headers=upload_headers, files=controlfile)
    r = requests.post(url=file_upload_url, data={'resource_type':'data'}, headers=upload_headers, files=datafile)
    r = requests.post(url=file_upload_url, data={'resource_type':'param'}, headers=upload_headers, files=paramfile)

    ###### Run Model
    modelrun_url = model_api_url+'/'+str(modelrun_id)+'/start'
    modelrun_headers={'Authorization': 'JWT %s' % token}
    r = requests.put(url=modelrun_url, headers=modelrun_headers)
    resp_dict = json.loads(r.content)
    task_id = resp_dict['modelrun']['task_id']

    if r.status_code == 200:
        print "\nModelrun Created.  Modelrun Id: {0}.  Task Id: {1}".format(modelrun_id, task_id)
        p.set(task_id, time.time())
        p.execute()   
        p1.set(task_id, modelrun_id)
        p1.execute()    

        task_model_map[task_id]=modelrun_id
        taskMap[task_id]=modelrun_id
        # modelrunId_starttime[modelrun_id] =  time.time()
        plot_tc(task_id, time.time())
    else:
        print "\nModel run creation resulted in an error. Please rectify the error and proceed..."

    end=time.time()
    duration = end-start
    return duration


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
            # ipv4_address='10.0.9.0/24',
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
    return redis.llen('celery')


def poisson_job_generator():
    modelno=0
    rateParameter = 1.0/float(360.0/81.0) # 20 is lambda
    while True:
        duration = create_model_run()
        modelno=modelno+1
        modelcount = modelno
        print"\nModel Created------at {}-------------- : {}".format(time.time(),modelno)
        # sleep(1)
        sl = random.expovariate(rateParameter)-duration
        if sl<0:
            sleep(0)
        else:
            sleep(sl)
        
        ############################################
        if modelno > 10:
            sys.exit(0)
        ############################################


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

    while (currentRentedModels<total_rented_modelruns_allowed):
        if queue_length()>0:
            worker_counter, duration = containerCreationSnippet(worker_counter)
            currentRentedModels =currentRentedModels+1

            print "\nTotal Models Allowed ", total_rented_modelruns_allowed 
            print "Rented Models Count: ", currentRentedModels 
            print "wastedChances-now* {} : {}".format(time.time(),wastedChances)

            while wastedChances>0 and currentRentedModels<total_rented_modelruns_allowed:
                if queue_length()>0:
                    worker_counter, duration = containerCreationSnippet(worker_counter)
                    currentRentedModels =currentRentedModels+1
                    wastedChances = wastedChances-1

        else:
            wastedChances = wastedChances+1

            ############################################
            if wastedChances>4:
                sys.exit(0)
            ############################################
        
            print "wastedChances-now {} : {}".format(time.time(),wastedChances)

        sl = time_interval-duration
        if sl<0:
            sleep(0)
        else:
            sleep(sl)

    while True:
        sys.exit(0)
    	pass
 


print "\n ******* Self Managed Worker System: Started *******"

print '\nTotal Money: ', total_money, '$'
print 'Rate of Container: ', container_rate_per_min,' $/min'
print 'Average time for modelrun : ', tavg_modelrun_secs,' sec'
print 'Maximum rented modelruns  : ', total_rented_modelruns_allowed
print 'Calculated time interval  : ', time_interval,' sec'
print 'Total Models Allowed ', total_rented_modelruns_allowed 

try:
    thread.start_new_thread(poisson_job_generator,())
    thread.start_new_thread(rentedContainerCreation,())
    thread.start_new_thread(plot_completedjobs_time,()) 

    while True:
        # sleep(2)
        # plot_finishedCount_qlen()

        for jobId in taskMap.copy():
            if AsyncResult(jobId).state == 'SUCCESS':
                if jobId not in completedjobs:
                    completedjobs.append(jobId)
                    taskMap.pop(jobId,0)
        
    


except (KeyboardInterrupt, SystemExit):
    sys.exit(0)
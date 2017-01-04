from __future__ import division
import os 
import docker
import docker.utils

import requests
import json
from celery import Celery

from sets import Set
from time import sleep
from celery.result import AsyncResult
from time import sleep
import docker
import docker.utils

# client = docker.Client()
# client = docker.DockerClient(base_url='unix://var/run/docker.sock')
# client = docker.Client(base_url='unix://var/run/docker.sock') #default

# client = docker.Client(base_url='http://10.0.9.13:2375', tls=False)
# print client.version()

# def create_model_run():
#     token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDgyOTkwNjkxLCJuYmYiOjE0ODI5OTA2OTEsImV4cCI6MTQ4NTU4MjY5MX0.Z7dfiT9o2oMT_fQzRvddrolwmG98r0TAJKcvwOD90IE'
#     payload = {'description': 'test_description', 'model_name': 'prms', 'title': 'test01'}
#     headers={'Content-Type':'application/json', 'Authorization': 'JWT %s' % token}

#     r = requests.post(url="http://192.168.99.101:5000/api/modelruns", json=payload, headers=headers)
#     resp_dict = json.loads(r.content)
#     modelrun_id = resp_dict['id']

#     print resp_dict

#     print r.status_code, r.reason
#     print resp_dict['id']

#     # # File Upload
#     payload = {'resource_type':'input'}
#     upload_headers={'Authorization': 'JWT %s' % token}
#     file_upload_url = 'http://192.168.99.101:5000/api/modelruns/'+str(modelrun_id)+'/upload'
#     control_file_name = '1-month_input/LC.control'
#     controlfile = {'file': open(control_file_name, 'rb')}
#     data_file_name = '1-month_input/data.nc'
#     datafile = {'file': open(data_file_name, 'rb')}
#     param_file_name = '1-month_input/parameter.nc'
#     paramfile = {'file': open(param_file_name, 'rb')}

#     r = requests.post(url=file_upload_url, data={'resource_type':'control'}, headers=upload_headers, files=controlfile)
#     #print r.status_code, r.reason  
#     # print r.content
#     r = requests.post(url=file_upload_url, data={'resource_type':'data'}, headers=upload_headers, files=datafile)
#     # print r.status_code, r.reason  
#     # print r.content
#     r = requests.post(url=file_upload_url, data={'resource_type':'param'}, headers=upload_headers, files=paramfile)
#     # print r.status_code, r.reason  
#     # print r.content

#     # run model
#     modelrun_url = 'http://192.168.99.101:5000/api/modelruns/'+str(modelrun_id)+'/start'
#     modelrun_headers={'Authorization': 'JWT %s' % token}
#     r = requests.put(url=modelrun_url, headers=modelrun_headers)
#     resp_dict = json.loads(r.content)
#     task_id = resp_dict['modelrun']['task_id']
#     print r.status_code, r.reason  
#     print r.content


#     if r.status_code == 200:
#         print "\nModelrun Created.  Modelrun Id: {0}.  Task Id: {1}".format(modelrun_id, task_id)

#     else:
#         print "\nModel run creation resulted in an error. Please rectify the error and proceed..."


# create_model_run()
def create_worker_container(container_name):
    client = docker.Client(base_url='http://10.0.9.16:2375', tls=False)
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
        command='celery -A worker.modelworker worker -Ofair --loglevel=info --autoreload --logfile=/celery.log -n '+ container_name,
        name=container_name,
        volumes=volumes,
        host_config=host_config,
        networking_config = networking_config
        # host_config=create_host_config(port_bindings={2424:2425})
        # host_config=docker.utils.create_host_config(binds=binds)
    ) 
 
    response = client.start(container=container.get('Id'))


create_worker_container('worker-3')

print "jose"


















# total_money = float(100)
# container_rate_per_min = float(1)
# tavg_modelrun_secs = float(8.35)
# tavg_modelrun_mins = float(tavg_modelrun_secs/60)
# total_rented_modelruns_allowed = int(total_money/(tavg_modelrun_mins*container_rate_per_min))
# # time interval calculated for one hour. i.e, we are distributing total_rented_modelruns_allowed among the one hour
# time_interval = float(60.0/total_rented_modelruns_allowed)
# time_interval=time_interval*60

# print '\nTotal Money: ', total_money, '$'
# print 'Rate of Container: ', container_rate_per_min,' $/min'
# print 'Average time for modelrun : ', tavg_modelrun_secs,' sec'
# print 'Maximum rented modelruns  : ', total_rented_modelruns_allowed
# print 'Calculated time interval  : ', time_interval,' sec'








# celery = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')

# container_name = 'worker-jose'

# environment = ['C_FORCE_ROOT=true','VWADAPTOR_CELERY_BROKER_URL=redis://workerdb:6379/0','VWADAPTOR_CELERY_RESULT_BACKEND=redis://workerdb:6379/0',
#               'VWADAPTOR_ENV=prod','VWADAPTOR_HOST=0.0.0.0','VWADAPTOR_JWT_AUTH_HEADER_PREFIX=JWT','VWADAPTOR_JWT_SECRET_KEY=virtualwatershed',
#               'VWADAPTOR_SECRET=vwadaptor','VWADAPTOR_SQLALCHEMY_DATABASE_URI=postgresql://postgres:postgres@modeldb:5432/postgres',
#               'VWADAPTOR_STORAGE_CONTAINER=/vwstorage','VWADAPTOR_STORAGE_EXTENSIONS=nc,control', 
#               'VWADAPTOR_STORAGE_PROVIDER=LOCAL','VWADAPTOR_STORAGE_SERVER=true',
#               'VWADAPTOR_STORAGE_SERVER_URL=/download','VWADAPTOR_USER_DATABASE_URI=postgresql://postgres:postgres@userdb:5432/postgres']

# links = [('postgres-modeldb', 'modeldb'),('postgres-userdb', 'userdb'),('redis-workerdb', 'workerdb')]

# volumes = {'/vwstorage': {'bind': '/vwstorage', 'mode': 'rw'}}
# networks = ['my-net']

# # container = client.containers.run(
# #      image='bfirsh/reticulate-splines', detach=True)

# host_config = client.create_host_config(
#         links=links,
#         # port_bindings = port_bindings
#     )

# container = client.containers.run(
#         # image='virtualwatershed/vwadaptor',
#         image ='josepainumkal/vwadaptor:jose_toolUI',
#         links =  links,
#         network_mode = 'my-net',
#         detach=True,
#         command ='celery -A worker.modelworker worker -Ofair --loglevel=info --autoreload --logfile=/celery.log -n '+ container_name,
#         environment = environment,
#         name = container_name,
#         volumes = volumes,
#         host_config=host_config
        
# ) 




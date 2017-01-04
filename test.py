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

client = docker.Client()

celery = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')


import os
from multiprocessing import Process, Value, Array, Manager




# os.system('sshpass -p "tcuser" rsync -a -e "ssh" --rsync-path="sudo rsync" /vwstorage/ docker@192.168.99.102:/vwstorage/')

rentedHostMachines =  Manager().dict()
rentedHostCredentials_1=['docker','tcuser'] 
rentedHostMachines['192.168.99.104'] = rentedHostCredentials_1

for ip in rentedHostMachines.copy():
    credentials = rentedHostMachines[ip]
    uname = credentials[0]
    pwd = credentials[1]
   
    addr = 'sshpass -p '+'"'+pwd+'"'+' rsync -a -e "ssh" --rsync-path="sudo rsync" /vwstorage/ '+uname+'@'+ip+':/vwstorage/'
    # print addr
    # os.system('sshpass -p "tcuser" rsync -a -e "ssh" --rsync-path="sudo rsync" /vwstorage/ docker@192.168.99.102:/vwstorage/')
    os.system(addr)




# resp = client.containers(all=True, filters={'status':'exited'})

# # list of exited containers
# exited_worker_containers = []

# for d in resp:
# 	data = json.dumps(d) 
# 	# print data[0]
# 	nameofContainer = json.loads(data)['Names'][0]
# 	if nameofContainer.startswith('/worker-'):
# 		exited_containers.append(nameofContainer.split('/')[1])
	
# print exited_worker_containers







# mydict = {'jose':'10','sumi':'12','minu':'12'}
# print mydict.keys()[mydict.values().index('9')] # 




# client = Client(base_url='unix://var/run/docker.sock')
# client = docker.Client()
# celery = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')
# i = celery.control.inspect()


# def create_worker_container(container_name):
#     container_envs = docker.utils.parse_env_file('/var/www/taskmanager/container_env.txt')
#     links=[('postgres-modeldb', 'modeldb'),('postgres-userdb', 'userdb'),('redis-workerdb', 'workerdb')]
#     binds={"/vwstorage": "/vwstorage"}
#     volumes = ['/vwstorage']

#     volume_bindings = {
#         '/vwstorage': {
#             'bind': '/vwstorage',
#             'mode': 'rw',
#         },
#     }

#     host_config = client.create_host_config(
#         binds=volume_bindings,
#         links=links,
#         # network_mode='container:[taskmanager1]'
#         # port_bindings = port_bindings
#     )


#     networking_config = client.create_networking_config({
#     'my-net': client.create_endpoint_config(
#         ipv4_address='10.0.9.13/24'
#     )
#     })


#     container = client.create_container(
#         # image='virtualwatershed/vwadaptor',
#         image='josepainumkal/vwadaptor:jose_toolUI',
#         environment=container_envs,
#         stdin_open=True,
#         tty=True,
#         command='celery -A worker.modelworker worker --loglevel=info --autoreload --logfile=/celery.log -n '+ container_name,
#         name=container_name,
#         volumes=volumes,
#         host_config=host_config,
#         networking_config=networking_config
        
#         # networking_config = networking_config
#         # host_config=create_host_config(port_bindings={2424:2425})
#         # host_config=docker.utils.create_host_config(binds=binds)
#     ) 
 
#     response = client.start(container=container.get('Id'))
#     print container.get('Id')


# create_worker_container('worker-1')
# print "ACTIVE: ",celery.control.inspect().active()
# create_worker_container('worker-1')
# sleep(5)

# print "ACTIVE: ",celery.control.inspect().active()

# create_worker_container('worker-2')
# sleep(5)

# print "ACTIVE: ",celery.control.inspect().active()
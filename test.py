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
import time

client = docker.Client()

celery = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')


import os
from multiprocessing import Process, Value, Array, Manager

overlay_network_name ='my-overlay'
volume_loc = '/var/nfs/vws/vwstorage'

def create_worker_container(container_name):
    start = time.time()

    baseurl= 'http://192.168.3.14:2375'
    client = docker.Client(base_url=baseurl, tls=False)

    container_envs = docker.utils.parse_env_file('/var/www/taskmanager/container_env.txt')
    links=[('postgres-modeldb', 'modeldb'),('postgres-userdb', 'userdb'),('redis-workerdb', 'workerdb')]
    # volumes = ['/vwstorage']
    volumes= [volume_loc]

    volume_bindings = {
        '/var/nfs/vws/vwstorage': {
            'bind': '/vwstorage',
            'mode': 'rw',
        },
    }

    host_config = client.create_host_config(
        binds=volume_bindings,
        links=links,
        network_mode=overlay_network_name
        # port_bindings = port_bindings
    )

    networking_config = client.create_networking_config({
        overlay_network_name: client.create_endpoint_config(
            # ipv4_address=overlay_network_ipv4Address,
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

    # client.connect_container_to_network(container=container.get('Id'), ipv4_address=overlay_network_ipv4Address)


create_worker_container('jose-5')
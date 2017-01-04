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


# print "ACTIVE: ",celery.control.inspect().active()
# print "SCHEDULE: ",celery.control.inspect().scheduled()
# print "REGISTERED: ",celery.control.inspect().registered()


celery.control.broadcast('shutdown', destination=['celery@worker-1'])
celery.control.broadcast('shutdown', destination=['celery@worker-2'])
celery.control.broadcast('shutdown', destination=['celery@worker-3'])
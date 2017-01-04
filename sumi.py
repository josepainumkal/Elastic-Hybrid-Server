from sets import Set
from time import sleep
from celery.result import AsyncResult
from time import sleep
import docker
import docker.utils
import os
from celery import Celery

celery = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')

print "ACTIVE: ",celery.control.inspect().active()
print "SCHEDULE: ",celery.control.inspect().scheduled()
print "REGISTERED: ",celery.control.inspect().registered()
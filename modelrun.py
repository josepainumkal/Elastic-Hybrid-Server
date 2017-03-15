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

import threading
from threading import Thread

from celery import Celery
from time import sleep
from multiprocessing import Process, Value, Array, Manager
from celery.result import AsyncResult
from redis import Redis


token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDg2NDEwMjAxLCJuYmYiOjE0ODY0MTAyMDEsImV4cCI6MTQ4NzI3NDIwMX0.K9HyjPcLgS3NxsWLUyP9sW6oJQU4I2rlA8qVWJE96tc'
model_api_url="http://134.197.42.21:5000/api/modelruns"


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
    else:
        print "\nModel run creation resulted in an error. Please rectify the error and proceed..."

    end=time.time()
    duration = end-start
    return duration


create_model_run()

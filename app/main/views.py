from __future__ import division
import json
import os
import urllib
import subprocess   
from datetime import datetime

from collections import defaultdict

from flask import current_app as app
from flask import redirect, render_template, session, request, flash, Response
from flask import send_file

from . import main
from .forms import SearchForm

from gstore_adapter.client import VWClient

from app import cache
from flask.ext.security import login_required, current_user
from functools import wraps
from flask_jwt import _default_jwt_encode_handler
from gstore_client import VWClient
import matplotlib.pyplot as plt

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

from .. import mail
from flask_mail import Message

import numpy as np


task_model_map = Manager().dict()
taskMap = Manager().dict()
new_workers = Manager().list()
modelrunId_starttime = Manager().dict()
jobid_jobstart = Manager().dict()
workerName_hostip = Manager().dict()
rented_hostips = Manager().list()
completedjobs = Manager().list()
rentedHostMachines =  Manager().dict()
paramteres_seams = Manager().dict()


##############################################################################################################

rented_hostips.append('http://10.0.9.10:2375')
rentedHostCredentials_1=['docker','tcuser'] 
rentedHostMachines['192.168.99.102'] = rentedHostCredentials_1

total_no_of_questions = 4
# sleep_email_alert = int(8)
barloc = '/var/www/taskmanager/app/static/'
file_loc = '/var/www/taskmanager/app/main/generated_FILES/'

# total_money = float(2.26)
# budget_period = float(6)
# lamda = float(80)
# container_rate_per_min = float(1.0)
# tavg_modelrun_secs = float(3.4)
# tavg_modelrun_mins = float(tavg_modelrun_secs/60)
# total_rented_modelruns_allowed = int(total_money/(tavg_modelrun_mins*container_rate_per_min))
# time_interval = float((budget_period*60)/total_rented_modelruns_allowed)

# time_interval = time_interval-0.08


##############################################################################################################

if not os.path.exists(file_loc):
    os.makedirs(file_loc)

celery = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')
redis = Redis(host='workerdb', port=6379, db=0)
redis1 = Redis(host='workerdb', port=6379, db=1)
redis3 = Redis(host='workerdb', port=6379, db=3)
p = redis.pipeline()
p1 = redis1.pipeline()
p3 = redis3.pipeline()

sleep_email_alert = float(redis3.get('email_interval'))


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
        links=links,
        network_mode='my-net'
        # port_bindings = port_bindings
    )

    container = client.create_container(
        # image='virtualwatershed/vwadaptor',
        image='josepainumkal/vwadaptor:jose_toolUI',
        environment=container_envs,
        stdin_open=True,
        tty=True,
        command='celery -A worker.modelworker worker -Ofair --loglevel=info --autoreload --logfile=/celery.log -n '+ container_name,
        name=container_name,
        volumes=volumes,
        host_config=host_config
        # networking_config = networking_config
        # host_config=create_host_config(port_bindings={2424:2425})
        # host_config=docker.utils.create_host_config(binds=binds)
    ) 
 
    response = client.start(container=container.get('Id'))
    # print container.get('Id')


@main.route('/worker')
def createworker():
    # return Response('Online: %s' % ', '.join(get_online_users()),
    #                 mimetype='text/plain')
    
    create_worker_container('worker-4')
    # resp = client.containers(filters={'name':'convtools'})

    # resp = json.dumps(resp)
    # # return Response(resp)

    # if resp =='[]':
    #     # the container is stopped/doesnot exist ( not present in 'docker ps')
    #     create_convtools_container()
    #     # sleep(3.5)
    #     # return Response('NO')

    # return redirect('http://vw-dev:5020/')
    return Response('CREATED')




def create_convtools_container():
    container_name = 'convtools'
    container_envs = docker.utils.parse_env_file('/var/www/taskmanager/env_vwtools.txt')
    links=[('postgres-userdb', 'userdb'),('postgres-webappdb', 'webappdb'),('redis-sessiondb', 'sessiondb')]
    
    host_config = client.create_host_config(
        links=links,
        port_bindings = {80:5020}
    )

    container = client.create_container(
        # image='virtualwatershed/vwadaptor',
        image='josepainumkal/convtools:jose_toolUI',
        environment=container_envs,
        stdin_open=True,
        tty=True,
        command='python manage.py runserver -h 0.0.0.0 -p 80',
        name=container_name,
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


def set_api_token(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if current_user and 'api_token' not in session:
            session['api_token'] = _default_jwt_encode_handler(current_user)
        return func(*args, **kwargs)
    return decorated

@main.route('/', methods=['GET'])
@login_required
@set_api_token
def toolset_index():
    return render_template('toolset/index.html')


@main.route('/vwppushmodels', methods=['GET'])
@login_required
@set_api_token
def vwppushmodels():
    # session['sampletest'] = 'hello';
    return render_template('vwppushmodels.html')





@main.route('/stasks', methods=['GET'])
def seams_tasks_info():
    # session['sampletest'] = 'hello';
    return render_template('s_tasks.html')


@main.route('/survey_results', methods=['GET'])
def survey_results():
    # session['sampletest'] = 'hello';
    return render_template('survey_results.html')


@main.route('/convtools')
def convtools():
    # return Response('Online: %s' % ', '.join(get_online_users()),
    #                 mimetype='text/plain')
    resp = client.containers(filters={'name':'convtools'})

    resp = json.dumps(resp)
    # return Response(resp)

    if resp =='[]':
        # the container is stopped/doesnot exist ( not present in 'docker ps')
        create_convtools_container()
        # sleep(3.5)
        # return Response('NO')

    return redirect('http://vw-dev:5020/')



@main.route('/seams')
def seams():
    return render_template('seams.html')

@main.route('/seams_update')
def seams_update():
    return render_template('seams_update.html')

@main.route('/seams_activate_page')
def seams_activate_page():
    return render_template('seams_activate.html')

@main.route('/survey')
def survey():
    return render_template('survey.html')



@main.route('/access_token')
@login_required
@set_api_token
def get_user_access_token():
    return session['api_token']


@main.route('/setGstoreCred', methods=['POST'])
@login_required
@set_api_token
def setGstoreCred():
    # Clearing earlier uname & pwd
    session.pop('g-uname', None)
    session.pop('g-pass', None)

    gstore_username = request.form['gstore-uname']
    gstore_password = request.form['gstore-pwd']

    # gstore_username = ""
    # gstore_password = ""
    # gstore_host_url = "https://vwp-dev.unm.edu/" #TODO: get this from config
    gstore_host_url = app.config['GSTORE_HOST']

    vwclient = VWClient(gstore_host_url, gstore_username, gstore_password)
    verified = vwclient.authenticate()
    if verified == True:
        session['g-uname'] = gstore_username
        session['g-pass'] = gstore_password
        return json.dumps({'status':'Success'});
    else:
        return json.dumps({'status':'Failed'});

   


@main.route('/search', methods=['GET', 'POST'])
def search():
    """
    Create model run panels, rectangles on the search/home page that display
    summary information about the data that the VW has for a particular model
    run.

    Returns: (str) HTML string of the model run panel
    """
    panels = []
    search_fields = ['model_run_name', 'researcher_name', 'model_keywords',
                     'description']
    search_results = []
    form = SearchForm(request.args)

    vw_client = VWClient(app.config['GSTORE_HOST'],
                         app.config['GSTORE_USERNAME'],
                         app.config['GSTORE_PASSWORD'])

    if request.args and not form.validate():
        flash('Please fill out at least one field')

        return render_template('search.html', form=form, panels=panels)
    if request.args:
        words = form.model_run_name.data.split()

    if request.args:
        for search_field in search_fields:
            search_args = defaultdict()
            for w in words:
                search_args[search_field] = w
                results = vw_client.modelrun_search(**search_args)
                search_results += results.records

    records = search_results
    if records:
        # make a panel of each metadata record
        panels = [_make_panel(rec) for rec in records if rec]

        panels = {p['model_run_uuid']: p for p in panels}.values()

    # pass the list of parsed records to the template to generate results page
    return render_template('search.html', form=form, panels=panels)

@main.route('/docs/vwpy', methods=['GET'])
def vwpydoc():
    return redirect('/static/docs/vwpy/index.html')

@main.route('/docs', methods=['GET'])
def docredir():
    return redirect('/static/docs/vwpy/index.html')


def _make_panel(search_record):
    """
    Extract fields we currently support from a single JSON metadata file and
    prepare them in dict form to render search.html.

    Returns: (dict) that will be an element of the list of panel_data to be
        displayed as search results
    """
    panel = {"keywords": search_record['Keywords'],
             "description": search_record['Description'],
             "researcher_name": search_record['Researcher Name'],
             "model_run_name": search_record['Model Run Name'],
             "model_run_uuid": search_record['Model Run UUID']}

    return panel


def find_user_folder():
    username = current_user.email
    # get the first part of username as part of the final file name
    username_part = username.split('.')[0]
    app_root = os.path.dirname(os.path.abspath(__file__))
    app_root = app_root + '/../static/user_data/' + username_part
    return app_root




def model_vwp_push(model_Id, model_type, model_desc, model_title, controlURL, dataURL, paramURL, statsURL, outURL, animationURL):  
    app_root = find_user_folder()
    if not os.path.exists(app_root):
        os.makedirs(app_root)

    # TODO clean the previous download input files
    data_file = app_root + app.config['TEMP_DATA']
    control_file = app_root + app.config['TEMP_CONTROL']
    param_file = app_root + app.config['TEMP_PARAM']
    animation_file = app_root + app.config['TEMP_ANIMATION']
    output_file = app_root + app.config['TEMP_OUTPUT']
    statvar_file = app_root + app.config['TEMP_STAT']

    vwp_push_info_file = app_root + app.config['VWP_PUSH_INFO']

    # clean up previous download file
    if os.path.isfile(data_file):
        os.remove(data_file)

    if os.path.isfile(control_file):
        os.remove(control_file)
        
    if os.path.isfile(param_file):
        os.remove(param_file)

    if os.path.isfile(animation_file):
        os.remove(animation_file)
    
    if os.path.isfile(output_file):
        os.remove(output_file)
    
    if os.path.isfile(statvar_file):
        os.remove(statvar_file)


    # download three inputs file based on the urls
    if controlURL is not None:
        urllib.urlretrieve(controlURL, control_file)
    if dataURL is not None:
        urllib.urlretrieve(dataURL, data_file)
    if paramURL is not None:
        urllib.urlretrieve(paramURL, param_file)
    if animationURL is not None:
        urllib.urlretrieve(animationURL, animation_file)
    if outURL is not None:
        urllib.urlretrieve(outURL, output_file)
    if statsURL is not None:
        urllib.urlretrieve(statsURL, statvar_file)

    # gstore testing - Start
    
    gstore_username = session['g-uname']
    gstore_password =  session['g-pass']
    gstore_host_url = app.config['GSTORE_HOST']


    vwclient = VWClient(gstore_host_url, gstore_username, gstore_password)
    vwclient.authenticate()
      
    resp = {}
    failed = []
    modeluuid_vwp = vwclient.createNewModelRun(model_Id, model_title, model_type, model_desc)
    if modeluuid_vwp!= '':
       
        # changing the working directory to upload folder path
        os.chdir(app_root)
        control_file = app.config['TEMP_CONTROL'].strip("/")
        data_file = app.config['TEMP_DATA'].strip("/")
        param_file = app.config['TEMP_PARAM'].strip("/")
        animation_file = app.config['TEMP_ANIMATION'].strip("/")
        output_file = app.config['TEMP_OUTPUT'].strip("/")
        statvar_file = app.config['TEMP_STAT'].strip("/")

        c = vwclient.uploadModelData_swift(modeluuid_vwp, control_file) #upload control file
        d = vwclient.uploadModelData_swift(modeluuid_vwp, data_file)    #upload data file
        p = vwclient.uploadModelData_swift(modeluuid_vwp, param_file)   #upload parameter file
       
        s = vwclient.uploadModelData_swift(modeluuid_vwp, statvar_file) #upload statvar file
        o = vwclient.uploadModelData_swift(modeluuid_vwp, output_file)  #upload output file
        if animationURL is not None:
            a = vwclient.uploadModelData_swift(modeluuid_vwp, animation_file)  #upload animation file
       


        # check for failure in upload
        if c.status_code !=200:
            failed.append('control')
        if d.status_code !=200:
            failed.append('data')
        if p.status_code !=200:
            failed.append('param')
        if s.status_code !=200:
            failed.append('statvar')
        if o.status_code !=200:
            failed.append('output')
        if animationURL is not None:
            if a.status_code !=200:
                failed.append('animation')

        current_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') 

        resp['modeluuid_vwp'] = modeluuid_vwp
        resp['pushed_time'] = current_time
        resp['model_Id'] = model_Id

        resp['control_file_status_code'] = c.status_code
        resp['data_file_status_code'] = d.status_code
        resp['param_file_status_code'] = p.status_code
        resp['statvar_file_status_code'] = s.status_code
        resp['output_file_status_code'] = o.status_code
        if animationURL is not None:
            resp['animation_file_status_code'] = a.status_code

        # test
        # resp['approot'] = app_root
        # resp['d_file'] = data_file


        # store it in a file
        with open(vwp_push_info_file, "a") as infoFile:
            infoFile.write('{}\t{}\t{}\t{}\t{}\n'.format(model_Id, modeluuid_vwp, current_time, failed, model_title))

    return resp

@main.route('/download_Model_Data', methods=['GET'])
@login_required
@set_api_token
def download_Model_Data():
    if request.method == 'GET':
        controlURL = request.args.get("controlURL")
        dataURL = request.args.get("dataURL")
        paramURL = request.args.get("paramURL")
        animationURL = request.args.get("animationURL")
        statsURL = request.args.get("statsURL")
        outURL = request.args.get("outURL")

        model_Id = request.args.get("model_Id")
        model_type = request.args.get("model_type")
        model_desc = request.args.get("model_desc")
        model_title = request.args.get("model_title")

        resp = model_vwp_push(model_Id, model_type, model_desc, model_title, controlURL, dataURL,paramURL, statsURL, outURL, animationURL)
        return json.dumps(resp)

# get info from the vwppush txt file
@main.route('/get_model_vwppush_details', methods=['GET'])
@login_required
@set_api_token
def vwp_push_details():
    if request.method == 'GET':
        # controlURL = request.args.get("controlURL")
        app_root = find_user_folder()
        vwp_push_info_file = app_root + app.config['VWP_PUSH_INFO']
        
        model_info={}
        
        if os.path.exists(vwp_push_info_file):
            with open(vwp_push_info_file, "r") as infoFile:
                for line in infoFile:
                    model_info_list=[]
                    values=line.split('\t')

                    model_info_list.append(values[1])
                    model_info_list.append(values[2])
                    model_info_list.append(values[3])
                    model_info[values[0]]=model_info_list

        return json.dumps(model_info)



# get info from the vwppush txt file
@main.route('/remove_vwp_push', methods=['GET'])
@login_required
@set_api_token
def vwp_push_remove():
    if request.method == 'GET':
        vwpModelId = request.args.get("vwpModelId")
        modelRunID = request.args.get("modelRunID")
        # gstore testing - Start
        # gstore_username = ""
        # gstore_password = ""
        # gstore_host_url = "https://vwp-dev.unm.edu/"

        gstore_username = session['g-uname']
        gstore_password = session['g-pass']
        gstore_host_url = app.config['GSTORE_HOST']


        vwclient = VWClient(gstore_host_url, gstore_username, gstore_password)
        vwclient.authenticate()
        result = vwclient.deleteModelRun(vwpModelId);
        
        if result==True:
            # delete from vwp-push-info file also
            app_root = find_user_folder()
            vwp_push_info_file = app_root + app.config['VWP_PUSH_INFO']
            if os.path.exists(vwp_push_info_file):
                f = open(vwp_push_info_file,"r")
                lines = f.readlines()
                f.close()
                f = open(vwp_push_info_file,"w")
                for line in lines:
                    values=line.split('\t')
                    if values[0]!=modelRunID:
                        f.write(line)
                f.close()
        return json.dumps(result)



# show task info for SEAMS 2017
@main.route('/resetTasks', methods=['POST'])
@login_required
@set_api_token
def resetTasks():
    redis3 = Redis(host='workerdb', port=6379, db=3)
    redis3.delete('finished_task_list');
    p3 = redis3.pipeline()
    models_owned = 0
    models_rented = 0
    p3.set('models_owned', int(models_owned))
    p3.set('models_rented', int(models_rented))
    p3.execute()

    return "success"


@main.route('/alert_email_list', methods=['GET'])
@login_required
@set_api_token
def alert_email_list():
    redis3 = Redis(host='workerdb', port=6379, db=3)
    p3 = redis3.pipeline()
    email_list=[]

    if request.method == 'GET':
        for i in redis3.smembers('alert_email_list'):
            email_list.append(i)
        return json.dumps(email_list)


@main.route('/emailSettings', methods=['GET'])
@login_required
@set_api_token
def emailSettings():
    redis3 = Redis(host='workerdb', port=6379, db=3)
    p3 = redis3.pipeline()
    resp={}

    resp['email_interval'] = redis3.get('email_interval')
    resp['fd_threshold'] = redis3.get('fd_threshold')
    resp['fd_score'] = redis3.get('fd_score')
    return json.dumps(resp)


@main.route('/modify_email_timeinterval', methods=['POST'])
@login_required
@set_api_token
def modify_email_timeinterval():
    new_interval = float(request.form.get('new_timeinterval'))
    redis3 = Redis(host='workerdb', port=6379, db=3)
    redis3.set('email_interval', new_interval)
    return 'success'

@main.route('/modify_threshold_score', methods=['POST'])
@login_required
@set_api_token
def modify_threshold_score():
    new_threshold = float(request.form.get('newthval'))
    redis3 = Redis(host='workerdb', port=6379, db=3)
    redis3.set('fd_threshold', new_threshold)
    return 'success'




@main.route('/add_email', methods=['POST'])
@login_required
@set_api_token
def add_email():
    email_id = request.form.get('addemail')
    redis3 = Redis(host='workerdb', port=6379, db=3)
    redis3.sadd('alert_email_list', email_id)
    return 'success'



@main.route('/del_email', methods=['POST'])
@login_required
@set_api_token
def del_email():
    email_id = request.form.get('delemail')
    redis3 = Redis(host='workerdb', port=6379, db=3)
    redis3.srem('alert_email_list', email_id)
    return 'success'


@main.route('/get_seams_tasks', methods=['GET'])
@login_required
@set_api_token
def get_seams_tasks():
    redis3 = Redis(host='workerdb', port=6379, db=3)
    p3 = redis3.pipeline()
    model_info=[]

    if request.method == 'GET':
        # controlURL = request.args.get("controlURL")
        # app_root = find_user_folder()
        # vwp_push_info_file = app_root + app.config['VWP_PUSH_INFO']
        
        len_tasks = redis3.llen('finished_task_list')
        for i in range(len_tasks):
            task_str = redis3.lindex('finished_task_list', i)
            values = task_str.split('|')
            taskId = values[0]
            modelId = values[1]
            waittime = values[2]
            runtime = values[3]
            workername = values[4]  
            amount_for_task = values[5]  

            if workername.split('@')[1].startswith('worker-'):
                worker_type = 'Rented'
            else:
                worker_type = 'Owned'


            model_info_list={}
            model_info_list['taskId'] = taskId
            model_info_list['modelId'] = modelId
            model_info_list['waittime'] = waittime
            model_info_list['runtime'] = runtime
            model_info_list['workername'] = workername
            model_info_list['workertype'] = worker_type
            model_info_list['amount_for_task'] = amount_for_task
            model_info.append(model_info_list)

        return json.dumps(model_info)



@main.route('/get_user_feedbacks', methods=['GET'])
@login_required
@set_api_token
def get_user_feedbacks():
    redis3 = Redis(host='workerdb', port=6379, db=3)
    p3 = redis3.pipeline()
    questionList=[]
    total_no_of_questions=4

    if request.method == 'GET':

        for x in range(1,(total_no_of_questions+1)):
            temp_question = {}
            key_name = 'q'+str(x)+'_info'
            temp_question['title'] = redis3.hget(key_name,'title')
            temp_question['option1'] = redis3.hget(key_name,'option1')
            temp_question['option2'] = redis3.hget(key_name,'option2')
            temp_question['option3'] = redis3.hget(key_name,'option3')
            temp_question['option1_count'] = redis3.hget(key_name,'option1_count')
            temp_question['option2_count'] = redis3.hget(key_name,'option2_count')
            temp_question['option3_count'] = redis3.hget(key_name,'option3_count')
            questionList.append(temp_question)

        return json.dumps(questionList)




@main.route('/get_seams_info', methods=['GET'])
@login_required
@set_api_token
def get_seams_info():
    redis3 = Redis(host='workerdb', port=6379, db=3)
    p3 = redis3.pipeline()
    if request.method == 'GET':
        budget_amount = redis3.get('budget_amount')
        amount_remaining = redis3.get('budget_amount_remaning')
        models_owned =  redis3.get('models_owned')
        models_rented = redis3.get('models_rented')
        instance_cost = redis3.get('instance_rate_per_hr')


        if models_owned is None:
            models_owned = 0
        if models_rented is None:
            models_rented=0
        if budget_amount is None:
            budget_amount=0
        if amount_remaining is None:
            amount_remaining=0
        if instance_cost is None:
            instance_cost = 0
            


        total_models = int(models_owned) + int(models_rented)

        seams_info = {}
        seams_info['budget_amount'] = budget_amount
        seams_info['amount_remaining'] = amount_remaining
        seams_info['models_owned'] = models_owned
        seams_info['models_rented'] = models_rented
        seams_info['instance_cost'] = instance_cost
        seams_info['total_models'] = total_models

        seams_info['lamda'] = redis3.get('lamda')
        seams_info['time_interval'] = redis3.get('time_interval')
        seams_info['total_rented_modelruns_allowed'] = redis3.get('total_rented_modelruns_allowed')
        seams_info['budget_period'] = redis3.get('budget_period')


    return json.dumps(seams_info)


def rsync_modelfiles():

    for ip in rentedHostMachines.copy():
        credentials = rentedHostMachines[ip]
        uname = credentials[0]
        pwd = credentials[1]
        addr = 'sshpass -p '+'"'+pwd+'"'+' rsync -a -e "ssh" --rsync-path="sudo rsync" /vwstorage/ '+uname+'@'+ip+':/vwstorage/'
        os.system(addr)

def plot_tc(taskId, createtime):
    plot_tcfile = file_loc+'c_task_createtime.txt'
    # plot_tcfile = '/var/www/taskmanager/app/main/'+'c_task_createtime.txt'
    with open(plot_tcfile, "a") as infoFile:
        infoFile.write('{}\t{}\n'.format(taskId,createtime))

def plot_completedjobs_time():
    while True:
        plot_completedjobs_time = file_loc+'c_finished_qlength.txt'
        # plot_completedjobs_time = '/var/www/taskmanager/app/main/'+'c_finished_qlength.txt'
        with open(plot_completedjobs_time, "a") as infoFile:
            infoFile.write('{}\t\t{}\t\t{}\n'.format(time.time(),len(completedjobs), queue_length()))
        sleep(2)

def create_model_run():
    start = time.time()

    token = paramteres_seams['token']
    model_api_url = paramteres_seams['model_api_url']

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
    control_file_name = '/var/www/taskmanager/app/main/1-month_input/LC.control'
    controlfile = {'file': open(control_file_name, 'rb')}
    data_file_name = '/var/www/taskmanager/app/main/1-month_input/data.nc'
    datafile = {'file': open(data_file_name, 'rb')}
    param_file_name = '/var/www/taskmanager/app/main/1-month_input/parameter.nc'
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


# @main.route('/send')
def send_email():
    alert_list = []
    redis3 = Redis(host='workerdb', port=6379, db=3)
    alert_email_list = redis3.smembers('alert_email_list')
    for i in alert_email_list:
        alert_list.append(i)

    sender = app.config['MAIL_USERNAME']
    # msg = Message("VW - Feedback Monitoring Alert",sender=sender,recipients=["josepainumkal@gmail.com"])
    msg = Message("VW - Feedback Monitoring Alert",sender=sender,recipients=alert_list)
    msg.body = "Alert"
    msg.html="<p>Hello, <p> The user feedbacks are getting worse. Please consider increasing the budget to improve the user experience on Virtual Watershed platform. <br>The user feedbacks are attached. <br><br>Thanks<br>Virtual Watershed"

    redis3 = Redis(host='workerdb', port=6379, db=3)
    p3 = redis3.pipeline()
    questionList=[]
    total_no_of_questions=4



    for x in range(1,(total_no_of_questions+1)):
        key_name = 'q'+str(x)+'_info'
        title = redis3.hget(key_name,'title')
        option1 = redis3.hget(key_name,'option1')
        option2 = redis3.hget(key_name,'option2')
        option3 = redis3.hget(key_name,'option3')
        option1_count = int(redis3.hget(key_name,'option1_count'))
        option2_count = int(redis3.hget(key_name,'option2_count'))
        option3_count = int(redis3.hget(key_name,'option3_count'))


        objects=(option1,option2,option3)
        counts = [option1_count,option2_count,option3_count]
        y_pos = np.arange(len(objects))
        fig_name = 'bar_'+str(x)+'.png'


        plt.bar(y_pos, counts, align='center')
        plt.xticks(y_pos,objects)
        plt.ylabel('Count')
        plt.xlabel('Options')
        plt.title(title)  
        plt.savefig(os.path.join(barloc, fig_name))
        
        with app.open_resource(os.path.join(barloc, fig_name)) as fp:
            msg.attach(os.path.join(barloc, fig_name), "image/png", fp.read())


    mail.send(msg)
    return "mailed"


def poisson_job_generator():
    modelno=0
    while True:
        duration = create_model_run()
        modelno=modelno+1
        modelcount = modelno
        print"\nModel Created------at {}-------------- : {}".format(time.time(),modelno)
        # sleep(1)
        rateParameter = paramteres_seams['rate_paramter'] 
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

    while (currentRentedModels < paramteres_seams['total_rented_modelruns_allowed']):
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

        sl = paramteres_seams['time_interval']- duration
        if sl<0:
            sleep(0)
        else:
            sleep(sl)

    while True:
        sys.exit(0)
        pass



def monitor_completedjobs():
    while True:
        for jobId in taskMap.copy():
            if celery.AsyncResult(jobId).state == 'SUCCESS':
                if jobId not in completedjobs:
                    completedjobs.append(jobId)
                    taskMap.pop(jobId,0)



@main.route('/seams_activate', methods=['POST'])
@login_required
@set_api_token
def seams_activate():
    redis3.set('fd_score', float(0))

    # cmd1 = ['python', '/var/www/taskmanager/app/main/example.py']
    # subprocess.Popen(cmd1)

    budget_amount = float(request.form.get('a_amount'))
    budget_period = float(request.form.get('a_duration'))
    rate = float(request.form.get('a_rate'))
    tavg = float(request.form.get('a_tavg'))
    lamda = float(request.form.get('a_lamda'))

    total_rented_time_sec = budget_amount*(1/rate)*3600
    total_rented_modelruns_allowed = total_rented_time_sec/tavg
    timeInterval_secs = (budget_period*60)/total_rented_modelruns_allowed


    p3.set('budget_amount', budget_amount)
    p3.set('budget_amount_remaning', budget_amount)
    p3.set('instance_rate_per_hr', rate)
    models_owned = 0
    models_rented = 0
    p3.set('models_owned', int(models_owned))
    p3.set('models_rented', int(models_rented))



    p3.set('time_interval', float(timeInterval_secs))
    p3.set('lamda', int(lamda))
    p3.set('total_rented_modelruns_allowed', int(total_rented_modelruns_allowed))
    p3.set('budget_period', int(budget_period))
    p3.execute()

    
    paramteres_seams['token'] = session['api_token'] 
    paramteres_seams['model_api_url'] = app.config['MODEL_HOST']+'/api/modelruns'
    paramteres_seams['time_interval'] = timeInterval_secs
    paramteres_seams['total_rented_modelruns_allowed'] = total_rented_modelruns_allowed
    paramteres_seams['budget_period'] = budget_period
    paramteres_seams['lamda'] = lamda
    paramteres_seams['rate_paramter'] = 1.0/float((budget_period*60.0)/paramteres_seams['lamda']) 


    print "\n ******* Self Managed Worker System: Started *******"

    print '\nTotal Money: ', budget_amount, '$'
    print 'Instance cost: ', rate,' $/hr'
    print 'Average time for modelrun : ', tavg,' sec'
    print 'Maximum rented modelruns  : ', total_rented_modelruns_allowed
    print 'Calculated time interval  : ', timeInterval_secs,' sec'
    print 'Total Models Allowed ', total_rented_modelruns_allowed 

    try:
        thread.start_new_thread(poisson_job_generator,())
        thread.start_new_thread(rentedContainerCreation,())
        thread.start_new_thread(plot_completedjobs_time,()) 
        thread.start_new_thread(monitor_completedjobs,()) 


        while True:
            sleep(sleep_email_alert)            
            send_mail_flag=0

            for x in range(1,(total_no_of_questions+1)):
                key_name = 'q'+str(x)+'_info'
                option1 = redis3.hget(key_name,'option1')
                option2 = redis3.hget(key_name,'option2')
                option3 = redis3.hget(key_name,'option3')
            
                if option1 is not None:
                    if option2 is not None:
                        if option3 is not None:

                            option1_count = int(redis3.hget(key_name,'option1_count'))
                            option2_count = int(redis3.hget(key_name,'option2_count'))
                            option3_count = int(redis3.hget(key_name,'option3_count'))

                            if x!=4 and max(option1_count,option2_count,option3_count) == option1_count:
                                send_mail_flag = send_mail_flag+1

            if send_mail_flag==3:
                # send_email()
                print "send mail"
                



    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)


    return session['api_token']


# show task info for SEAMS 2017
@main.route('/seams_update_info', methods=['POST'])
@login_required
@set_api_token
def seams_update_info():
    redis3.set('fd_score', float(0))

    budget_amount = float(request.form.get('totalamount'))
    budget_period = float(request.form.get('duration'))
    rate = float(request.form.get('rate'))
    tavg = float(request.form.get('tavg'))
    lamda = float(request.form.get('lamda'))
    
    budget_amount_remaning = float(redis3.get('budget_amount_remaning'))
    total_budget_amount = budget_amount + budget_amount_remaning

    # budget period is not constantly updated. 
    # total_budget_period_mins = float(paramteres_seams['budget_period']) + budget_period
    total_budget_period_mins = budget_period


    total_rented_time_sec = total_budget_amount*(1/rate)*3600
    total_rented_modelruns_allowed = total_rented_time_sec/tavg
    timeInterval_secs = (total_budget_period_mins*60)/total_rented_modelruns_allowed


    # p3.set('time_interval', float(timeInterval_secs))
    # p3.set('lamda', int(lamda))
    # p3.set('total_rented_modelruns_allowed', int(total_rented_modelruns_allowed))
    # p3.set('budget_period', int(budget_period))
    # p3.execute()


    paramteres_seams['budget_period'] = total_budget_period_mins
    paramteres_seams['time_interval'] = timeInterval_secs
    paramteres_seams['total_rented_modelruns_allowed'] = total_rented_modelruns_allowed
    paramteres_seams['lamda']=lamda
    paramteres_seams['rate_paramter'] = 1.0/float((total_budget_period_mins*60.0)/paramteres_seams['lamda']) 

    p3.set('budget_amount', total_budget_amount)
    p3.set('budget_amount_remaning', total_budget_amount)
    p3.set('instance_rate_per_hr', rate)


    p3.set('time_interval', float(timeInterval_secs))
    p3.set('lamda', int(lamda))
    p3.set('total_rented_modelruns_allowed', int(total_rented_modelruns_allowed))
    p3.set('budget_period', int(total_budget_period_mins))
    p3.execute()

    #show details on update page

    # tavg_for_owned = 8.7
    # mu_owned = (total_budget_period_mins *60.0)/tavg_for_owned
    # mu_rented = (total_budget_period_mins *60.0)/timeInterval_secs
    # total_mu = mu_owned + mu_rented;
    # rho = float(lamda*1.0/total_mu);
    # length_system =float(rho/(1-rho));
    # length_queue = length_system-rho;
    # waiting_queue = float(length_queue/lamda);
    # waiting_system = float(length_system/lamda);
    # length_queue = length_queue/(total_budget_period_mins *60.0);

    resp = {}
    resp["total_budget_amount"] = total_budget_amount
    resp["total_budget_period"] = total_budget_period_mins
    resp["time_interval"] =  timeInterval_secs
    resp["total_rented_modelruns_allowed"] = int(total_rented_modelruns_allowed)
    resp["instance_cost"] = rate
    resp["lamda"] = lamda

    # resp["expected_wait_time"] = waiting_queue
    # resp["expected_queue_length"] = length_queue

    return json.dumps(resp)




@main.route('/survey_submit', methods=['POST'])
@login_required
@set_api_token
def survey_submit():

    fd_score = float(redis3.get('fd_score'))

    q1 = request.form.get('q1') 
    key_name = 'q1_info'
    option_name = 'option'+str(q1)+'_count'
    option_weight = 'option'+str(q1)+'_weight'
    update_val = int(redis3.hget(key_name, option_name)) +1
    redis3.hmset(key_name,{option_name:update_val})


    q_weight = float(redis3.hget(key_name, 'weight'))
    option_weight = float(redis3.hget(key_name, option_weight))
    fd_score = fd_score + (q_weight*option_weight)

    q2 = request.form.get('q2') 
    key_name = 'q2_info'
    option_name = 'option'+str(q2)+'_count'
    option_weight = 'option'+str(q2)+'_weight'
    update_val = int(redis3.hget(key_name, option_name)) +1
    redis3.hmset(key_name,{option_name:update_val})

    q_weight = float(redis3.hget(key_name, 'weight'))
    option_weight = float(redis3.hget(key_name, option_weight))
    fd_score = fd_score + (q_weight*option_weight)


    q3 = request.form.get('q3') 
    key_name = 'q3_info'
    option_name = 'option'+str(q3)+'_count'
    option_weight = 'option'+str(q3)+'_weight'
    update_val = int(redis3.hget(key_name, option_name)) +1
    redis3.hmset(key_name,{option_name:update_val})

    q_weight = float(redis3.hget(key_name, 'weight'))
    option_weight = float(redis3.hget(key_name, option_weight))
    fd_score = fd_score + (q_weight*option_weight)



    q4 = request.form.get('q4') 
    key_name = 'q4_info'
    option_name = 'option'+str(q4)+'_count'
    option_weight = 'option'+str(q4)+'_weight'
    update_val = int(redis3.hget(key_name, option_name)) +1
    redis3.hmset(key_name,{option_name:update_val})

    q_weight = float(redis3.hget(key_name, 'weight'))
    option_weight = float(redis3.hget(key_name, option_weight))
    fd_score = fd_score + (q_weight*option_weight)

    redis3.set('fd_score', fd_score)

    return "success"




        
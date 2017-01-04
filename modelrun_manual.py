import requests
import json
import os 

taskid = []

# token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDgxNjY3Mzc3LCJuYmYiOjE0ODE2NjczNzcsImV4cCI6MTQ4NDI1OTM3N30.UTUjBQu9s0RHK2xxDFGYRjwtOoRRb4boXUpxGsz6m1Q'
# payload = {'description': 'test_description', 'model_name': 'prms', 'title': 'test01'}
# headers={'Content-Type':'application/json', 'Authorization': 'JWT %s' % token}

# r = requests.post(url="http://192.168.99.100:5000/api/modelruns", json=payload, headers=headers)
# resp_dict = json.loads(r.content)
# modelrun_id = resp_dict['id']

# print r.status_code, r.reason
# print resp_dict['id']

# # File Upload
# payload = {'resource_type':'input'}
# upload_headers={'Authorization': 'JWT %s' % token}
# file_upload_url = 'http://192.168.99.100:5000/api/modelruns/'+str(modelrun_id)+'/upload'
# control_file_name = '1-month_input/LC.control'
# controlfile = {'file': open(control_file_name, 'rb')}
# data_file_name = '1-month_input/data.nc'
# datafile = {'file': open(data_file_name, 'rb')}
# param_file_name = '1-month_input/parameter.nc'
# paramfile = {'file': open(param_file_name, 'rb')}

# r = requests.post(url=file_upload_url, data={'resource_type':'control'}, headers=upload_headers, files=controlfile)
# print r.status_code, r.reason  
# print r.content
# r = requests.post(url=file_upload_url, data={'resource_type':'data'}, headers=upload_headers, files=datafile)
# print r.status_code, r.reason  
# print r.content
# r = requests.post(url=file_upload_url, data={'resource_type':'param'}, headers=upload_headers, files=paramfile)
# print r.status_code, r.reason  
# print r.content

# # run model
# modelrun_url = 'http://192.168.99.100:5000/api/modelruns/'+str(modelrun_id)+'/start'
# modelrun_headers={'Authorization': 'JWT %s' % token}
# r = requests.put(url=modelrun_url, headers=modelrun_headers)
# resp_dict = json.loads(r.content)
# task_id = resp_dict['modelrun']['task_id']
# print r.status_code, r.reason  
# print r.content

# # store it in a file
# modeltaskdetails = '/var/www/taskmanager'+'/modeltaskdetails.txt'
# with open(modeltaskdetails, "a") as infoFile:
#     infoFile.write('{}\t{}\n'.format(task_id, modelrun_id))



# token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDgxNjY3Mzc3LCJuYmYiOjE0ODE2NjczNzcsImV4cCI6MTQ4NDI1OTM3N30.UTUjBQu9s0RHK2xxDFGYRjwtOoRRb4boXUpxGsz6m1Q'
# payload = {'description': 'test_description', 'model_name': 'prms', 'title': 'test01'}
# headers={'Content-Type':'application/json', 'Authorization': 'JWT %s' % token}
# upload_headers={'Authorization': 'JWT %s' % token}
# modelrun_headers={'Authorization': 'JWT %s' % token}
# control_file_name = '1-month_input/LC.control'
# data_file_name = '1-month_input/data.nc'
# param_file_name = '1-month_input/parameter.nc'
# controlfile = {'file': open(control_file_name, 'rb')}
# datafile = {'file': open(data_file_name, 'rb')}
# paramfile = {'file': open(param_file_name, 'rb')}




def create_model_run():
    # r = requests.post(url="http://192.168.99.100:5000/api/modelruns", json=payload, headers=headers)
    # resp_dict = json.loads(r.content)
    # modelrun_id = resp_dict['id']

    # file_upload_url = 'http://192.168.99.100:5000/api/modelruns/'+str(modelrun_id)+'/upload'
    # r = requests.post(url=file_upload_url, data={'resource_type':'control'}, headers=upload_headers, files=controlfile)
    # r = requests.post(url=file_upload_url, data={'resource_type':'data'}, headers=upload_headers, files=datafile)
    # r = requests.post(url=file_upload_url, data={'resource_type':'param'}, headers=upload_headers, files=paramfile)

    # modelrun_url = 'http://192.168.99.100:5000/api/modelruns/'+str(modelrun_id)+'/start'
    # r = requests.put(url=modelrun_url, headers=modelrun_headers)
    # task_id = resp_dict['modelrun']['task_id']
    
    # if r.status_code == 200:
    #     print "---Modelrun Created------Modelrun Id: {0}-------Task Id: {1}".format(modelrun_id, task_id)
    #     task_model_map[task_id]=modelrun_id
    # else:
    #     print "Model run creation resulted in an error. Please rectify the error and proceed..."
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDgxNjY3Mzc3LCJuYmYiOjE0ODE2NjczNzcsImV4cCI6MTQ4NDI1OTM3N30.UTUjBQu9s0RHK2xxDFGYRjwtOoRRb4boXUpxGsz6m1Q'
    payload = {'description': 'test_description', 'model_name': 'prms', 'title': 'test01'}
    headers={'Content-Type':'application/json', 'Authorization': 'JWT %s' % token}

    r = requests.post(url="http://192.168.99.100:5000/api/modelruns", json=payload, headers=headers)
    resp_dict = json.loads(r.content)
    modelrun_id = resp_dict['id']

    print r.status_code, r.reason
    print resp_dict['id']

    # File Upload
    payload = {'resource_type':'input'}
    upload_headers={'Authorization': 'JWT %s' % token}
    file_upload_url = 'http://192.168.99.100:5000/api/modelruns/'+str(modelrun_id)+'/upload'
    control_file_name = '1-month_input/LC.control'
    controlfile = {'file': open(control_file_name, 'rb')}
    data_file_name = '1-month_input/data.nc'
    datafile = {'file': open(data_file_name, 'rb')}
    param_file_name = '1-month_input/parameter.nc'
    paramfile = {'file': open(param_file_name, 'rb')}

    r = requests.post(url=file_upload_url, data={'resource_type':'control'}, headers=upload_headers, files=controlfile)
    print r.status_code, r.reason  
    print r.content
    r = requests.post(url=file_upload_url, data={'resource_type':'data'}, headers=upload_headers, files=datafile)
    print r.status_code, r.reason  
    print r.content
    r = requests.post(url=file_upload_url, data={'resource_type':'param'}, headers=upload_headers, files=paramfile)
    print r.status_code, r.reason  
    print r.content

    # run model
    modelrun_url = 'http://192.168.99.100:5000/api/modelruns/'+str(modelrun_id)+'/start'
    modelrun_headers={'Authorization': 'JWT %s' % token}
    r = requests.put(url=modelrun_url, headers=modelrun_headers)
    resp_dict = json.loads(r.content)
    task_id = resp_dict['modelrun']['task_id']
    taskid.append(task_id)
    print r.status_code, r.reason  
    print r.content

    if r.status_code == 200:
        print "---Modelrun Created------Modelrun Id: {0}-------Task Id: {1}".format(modelrun_id, task_id)
        # task_model_map[task_id]=modelrun_id
    else:
        print "Model run creation resulted in an error. Please rectify the error and proceed..."



# create_model_run()

##delete model 
# modelrun_id = 148
# modelrun_headers={'Content-Type':'application/json','Authorization': 'JWT %s' % token}
# deletemodel_url= 'http://192.168.99.100:5000/api/modelruns/'+str(modelrun_id)
# r = requests.delete(url=deletemodel_url, headers=modelrun_headers)
# print r.status_code, r.reason  
# print r.content
for _ in range(10):
    create_model_run()

print taskid


# while True:
#     create_model_run()

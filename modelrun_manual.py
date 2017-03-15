import requests
import json
import os 

taskid = []

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDg5NTI1MTgxLCJuYmYiOjE0ODk1MjUxODEsImV4cCI6MTQ5MDM4OTE4MX0.ZIRxnnn02GqOOEsgE1eX-pksTy3EWM2VHI1BI1xhkvE'

model_api_url="http://192.168.99.101:5000/api/modelruns"

def create_model_run():
    

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
    # control_file_name = '1-month_input/LC.control'

    
    # control_file_name = 'rui_data/LC.control'
    # data_file_name = 'rui_data/data.nc'
    # param_file_name = 'rui_data/parameter.nc'

    control_file_name = '1-month_input/LC.control'
    data_file_name = '1-month_input/data.nc'
    param_file_name = '1-month_input/parameter.nc'

    

    controlfile = {'file': open(control_file_name, 'rb')}

    datafile = {'file': open(data_file_name, 'rb')}

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

   
create_model_run()

# for _ in range(10):
#     create_model_run()

# print taskid


# while True:
#     create_model_run()

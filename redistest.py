from redis import Redis
import json

redis3 = Redis(host='workerdb', port=6379, db=3)
p3 = redis3.pipeline()


     
# newItem = []
# newItem.append("jose@gmail.com")
# redis3.lpush('alert_email_list',*newItem)

# newItem = []
# newItem.append("sumi@gmail.com")
# redis3.lpush('alert_email_list',*newItem)

# redis3.sadd('alert_email_list', 'jose@gmail.com')
# redis3.sadd('alert_email_list', 'sumi@gmail.com')
# redis3.sadd('alert_email_list', 'minu@gmail.com')


# # print "\t\t\alert_email_list: ",redis3.get('alert_email_list')
# # print"\nBefore:"
# # for i in range(redis3.scard('alert_email_list')):
# # 	print redis3.spop('alert_email_list')

# # redis3.srem('alert_email_list', 'mnu@gmail.com')

# # print"\nAfter:"
# # for i in range(redis3.scard('alert_email_list')):
# # 	print redis3.spop('alert_email_list')


# ex=redis3.smembers('alert_email_list')
# for i in ex:
# 	print i
# print ex








# redis3.hmset('q1_info',{'title':'Are you happy?', 'option1':'Agree', 'option2':'Disagree', 'option3':'Cannot say'})

# print redis3.hget('q1_info', 'title')

# # redis3.hset('question1', {'title':'Are you mad?'})

# # print redis3.hget('question1', 'title')

# print redis3.hget('q1_info', 'title')
# print redis3.hget('q1_info', 'option1')
# print redis3.hget('q1_info', 'option2')
# print redis3.hget('q1_info', 'option3')

# # redis3.hmset('question1',{'title':'Are you mad?', 'option1':'Agree', 'option2':'Disagree', 'option3':'Cannot say'})

# redis3.hmset('q1_info',{'title':'Are you mad ?'})

# # print redis3.hget('question1', 'title')
# # print redis3.hget('question1', 'option1')
# # print redis3.hget('question1', 'option2')
# # print redis3.hget('question1', 'option3')


# # redis3.hmset('q1_count',{'option1_count':0, 'option2_count':0, 'option3_count':0, 'option4_count':0})

# val = int(redis3.hget('q1_count', 'option1_count')) +1

# redis3.hmset('q1_count',{'option1_count':val})


# print redis3.hget('q1_info', 'title')
# print redis3.hget('q1_count', 'option1_count')
# print redis3.hget('q1_count', 'option2_count')
# print redis3.hget('q1_count', 'option3_count')

#################################################################################################################################################################################################################


# redis3.hmset('q1_info',{'title':'Are you satisfied with the website service?', 'option1':'Slow', 'option2':'Just fine', 'option3':'Good', 'option1_count':0, 'option2_count':0, 'option3_count':0 })
# redis3.hmset('q2_info',{'title':'Are you satisfied with the waiting (queuing) time?', 'option1':'Slow', 'option2':'Just fine', 'option3':'Good', 'option1_count':0, 'option2_count':0, 'option3_count':0 })
# redis3.hmset('q3_info',{'title':'Does the website respond your request fast enough?', 'option1':'Slow', 'option2':'Just fine', 'option3':'Good', 'option1_count':0, 'option2_count':0, 'option3_count':0 })
# redis3.hmset('q4_info',{'title':'Do you think the service is expensive??', 'option1':'No', 'option2':'Yes', 'option3':'Moderate', 'option1_count':0, 'option2_count':0, 'option3_count':0 })

redis3.hmset('q1_info',{'title':'Are you satisfied with the website service?', 'option1':'Yes', 'option2':'Just Fine', 'option3':'No', 'option1_count':0, 'option2_count':0, 'option3_count':0, 'option1_weight':-1,'option2_weight':0,'option3_weight':1, 'weight':0.2 })
redis3.hmset('q2_info',{'title':'Are you satisfied with the waiting (queuing) time?', 'option1':'Yes', 'option2':'Just fine', 'option3':'No', 'option1_count':0, 'option2_count':0, 'option3_count':0, 'option1_weight':-1,'option2_weight':0,'option3_weight':1, 'weight':0.8 })
redis3.hmset('q3_info',{'title':'Does the website respond your request fast enough?', 'option1':'Yes', 'option2':'Just fine', 'option3':'No', 'option1_count':0, 'option2_count':0, 'option3_count':0, 'option1_weight':-1,'option2_weight':0,'option3_weight':1, 'weight':0.3})
redis3.hmset('q4_info',{'title':'Do you want to pay more to have a faster service?', 'option1':'Yes', 'option2':'May be', 'option3':'No', 'option1_count':0, 'option2_count':0, 'option3_count':0, 'option1_weight':1,'option2_weight':0,'option3_weight':-1, 'weight':0.9})

redis3.set('fd_score', float(0))



# fd_score = float(redis3.get('fd_score'))



# q3 = 1
# key_name = 'q3_info'
# option_name = 'option'+str(q3)+'_count'
# option_weight = 'option'+str(q3)+'_weight'
# update_val = int(redis3.hget(key_name, option_name)) +1
# redis3.hmset(key_name,{option_name:update_val})

# q_weight = float(redis3.hget(key_name, 'weight'))
# option_weight = float(redis3.hget(key_name, option_weight))

# print 'q_weight:', q_weight, 'option_weight: ',option_weight
# fd_score = fd_score + (q_weight*option_weight)

# print fd_score


# redis3.set('fd_score', fd_score)

# print redis3.get('fd_score')










# redis3 .delete('q1_info')
# redis3 .delete('q2_info')
# redis3 .delete('q3_info')
# redis3 .delete('q4_info')


# redis3.hmset('q1_info',{'title':'Are you satisfied with the website service?', 'option1':'Slow', 'option2':'Just fine', 'option3':'Good', 'option1_count':0, 'option2_count':0, 'option3_count':0 })
# redis3.hmset('q2_info',{'title':'Are you satisfied with the waiting (queuing) time?', 'option1':'Slow', 'option2':'Just fine', 'option3':'Good', 'option1_count':0, 'option2_count':0, 'option3_count':0 })
# redis3.hmset('q3_info',{'title':'Does the website respond your request fast enough?', 'option1':'Slow', 'option2':'Just fine', 'option3':'Good', 'option1_count':0, 'option2_count':0, 'option3_count':0 })
# redis3.hmset('q4_info',{'title':'Do you want to pay more to have a faster service?', 'option1':'No', 'option2':'Not Sure', 'option3':'Yes', 'option1_count':0, 'option2_count':0, 'option3_count':0 })

# print redis3.hget('q1_info', 'title')
# print redis3.hget('q2_info', 'title')
# print redis3.hget('q3_info', 'title')
# print redis3.hget('q4_info', 'title')


# print redis3.hget('q1_info', 'option1')





# p = redis.pipeline()
# p.set('MaxRentedModelsAllowed', 3200)
# p.set('CurrentRentedModels', 200)
# p.execute()

# print redis.get('worker-1')
# print redis.get('worker-2')

# redis.delete('CurrentRentedModels')

# print redis.get('MaxRentedModelsAllowed')
# print redis.get('CurrentRentedModels')

# tasklist = []
# tasklist.append('jose')
# tasklist.append('amulya')
# tasklist.append('debra')

# redis.lpush('tasklist',*tasklist)
# print redis.llen('tasklist')
# redis.delete('tasklist')
# newItem = []
# newItem.append('THOMASmercymmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuiiii||||||||||||||||||ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd')
# redis.lpush('tasklist',*newItem)

# print redis3.get('budget_amount_remaning')


# for i in range(redis3.llen('finished_task_list')):
# 	print redis3.lindex('finished_task_list', i)

# redis3.delete('finished_task_list')

# def get_seams_tasks():
#     redis3 = Redis(host='workerdb', port=6379, db=3)
#     p3 = redis3.pipeline()
#     model_info=[]

        
#     len_tasks = redis3.llen('finished_task_list')
#     for i in range(len_tasks):
#        	task_str = redis3.lindex('finished_task_list', i)
#         values = task_str.split('|')
#         taskId = values[0]
#         modelId = values[1]
#         waittime = values[2]
#         runtime = values[3]
#         workername = values[4]  

#         if workername.split('@')[1].startswith('worker-'):
#             worker_type = 'Owned'
#         else:
#             worker_type = 'Rented'


#         model_info_list={}
#         model_info_list['taskId'] = taskId
#         model_info_list['modelId'] = modelId
#         model_info_list['waittime'] = waittime
#         model_info_list['runtime'] = runtime
#         model_info_list['workername'] = workername
#         model_info_list['workertype'] = worker_type
#         model_info.append(model_info_list)



#     print json.dumps(model_info)

# # get_seams_tasks()

# def get_seams_info():
#     redis3 = Redis(host='workerdb', port=6379, db=3)
#     p3 = redis3.pipeline()
#     budget_amount = redis3.get('budget_amount')
#     amount_remaining = redis3.get('budget_amount_remaning')
#     models_owned =  redis3.get('models_owned')
#     models_rented = redis3.get('models_rented')
#     container_rate = redis3.get('container_rate_per_min')
#     print models_owned
#     total_models = int(models_owned) + int(models_owned)

#     seams_info = {}
#     seams_info['budget_amount'] = budget_amount
#     seams_info['amount_remaining'] = amount_remaining
#     seams_info['models_owned'] = models_owned
#     seams_info['models_rented'] = models_rented
#     seams_info['container_rate'] = container_rate
#     seams_info['total_models'] = total_models

#     print json.dumps(seams_info)

# # get_seams_info()
# import time
# redis3 = Redis(host='workerdb', port=6379, db=3)
# p3 = redis3.pipeline()
# total_no_of_questions = 4


# while True:
#     # execute every 10 seconds
#     time.sleep(10)            
#     send_mail_flag=0

#     for x in range(1,(total_no_of_questions+1)):
#         key_name = 'q'+str(x)+'_info'
#         option1 = redis3.hget(key_name,'option1')
#         option2 = redis3.hget(key_name,'option2')
#         option3 = redis3.hget(key_name,'option3')
    
#         if option1 is not None:
#         	if option2 is not None:
#         		if option3 is not None:
#         			if x!=4 and max(option1,option2,option3) == option1:
#         				send_mail_flag = send_mail_flag+1

#     if send_mail_flag==3:
#         print 'send_email()'
# import pygal        

# line_chart = pygal.HorizontalBar()
# line_chart.title = 'Browser usage in February 2012 (in %)'
# line_chart.add('IE', 19.5)
# line_chart.add('Firefox', 36.6)
# line_chart.add('Chrome', 36.3)
# line_chart.add('Safari', 4.5)
# line_chart.add('Opera', 2.3)
# # line_chart.render()

# line_chart.render_to_file('bar_chart.html')
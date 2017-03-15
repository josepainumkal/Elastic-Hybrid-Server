from sets import Set
from time import sleep
from celery.result import AsyncResult
from time import sleep
import docker
import docker.utils
import os
from celery import Celery
from redis import Redis
import time


celery = Celery('vwadaptor', broker='redis://workerdb:6379/0',backend='redis://workerdb:6379/0')

print "ACTIVE: ",celery.control.inspect().active()
print "SCHEDULE: ",celery.control.inspect().scheduled()
print "REGISTERED: ",celery.control.inspect().registered()


# total_budget = float(1.607)
# print total_budget
# count = 0
# div = float(4.256 * 34/3600)
# print "price of one model", div

# while total_budget>0:
# 	total_budget = total_budget - div
# 	count = count+1
# 	print total_budget


# print "Count", count


# total_budget = float(1.63)
# instance_rate = float(4.256)
# tavg_modelrun_secs = float(34)
# tavg_modelrun_mins = float(tavg_modelrun_secs/60)
# tavg_modelrun_hr = float(tavg_modelrun_mins/60)

# total_rented_modelruns_allowed = int(total_budget/(instance_rate*tavg_modelrun_hr))

# budget_period_min = float(20)
# budget_period_hr = float(budget_period_min/60)
# budget_period_sec = float(budget_period_min*60)

# time_interval_hr = float(budget_period_hr/total_rented_modelruns_allowed)
# time_interval_min = float(time_interval_hr*60)
# time_interval_sec = float(time_interval_min*60)


# mu_own = float(budget_period_min*60/tavg_modelrun_secs)
# mu_rent = float(budget_period_min*60/time_interval_sec)
# mu = mu_own+mu_rent
# lamda = int(mu)



# time_interval = time_interval_sec


# print "total_budget", total_budget
# print "instance_rate", instance_rate
# print "tavg_modelrun_secs", tavg_modelrun_secs
# print "total_rented_modelruns_allowed", total_rented_modelruns_allowed
# print "budget_period_min", budget_period_min
# print "budget_period_sec", budget_period_sec
# print "time_interval_sec", time_interval_sec
# print "mu_own", mu_own
# print "mu_own", mu_rent
# print "mu", mu
# print "lamda", lamda


# runtime = float(34)
# runtime_hr = float(runtime/3600)
# amount_for_task = float(instance_rate*runtime_hr)

# amount_remaining = total_budget - amount_for_task

# print "amount_remaining", amount_remaining
# print "amount_for_task", amount_for_task
# print "runtime_hr", runtime_hr
# print "instance_rate", instance_rate




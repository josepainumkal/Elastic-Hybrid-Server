from __future__ import division
import math
import random


def nextTime(rateParameter):
    return -math.log(1.0 - random.random()) / rateParameter


rateParameter = 1.0/float(60/20)

# print rateParameter
# print nextTime(rateParameter)
# print nextTime(rateParameter)
# print nextTime(rateParameter)
# print nextTime(rateParameter)
# print nextTime(rateParameter)

# print nextTime(rateParameter)
# print nextTime(rateParameter)
# print nextTime(rateParameter)
# print nextTime(rateParameter)
# print nextTime(rateParameter)

# print nextTime(rateParameter)
# print nextTime(rateParameter)
# print nextTime(rateParameter)
# print nextTime(rateParameter)
# print nextTime(rateParameter)

# print nextTime(rateParameter)
# print nextTime(rateParameter)
# print nextTime(rateParameter)
# print nextTime(rateParameter)
# print nextTime(rateParameter)

sum=0
for _ in range(20):
    # sum =sum+nextTime(rateParameter)
    print random.expovariate(rateParameter)

print sum
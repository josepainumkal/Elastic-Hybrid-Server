import time
import multiprocessing
from multiprocessing import Process, Value, Array, Manager

mylist = Manager().list()
mydict = Manager().dict()

 
def my_function():
    # time.sleep(3)

    while True:
        # time.sleep(2)
        x=0
        while(x<100):
            time.sleep(1)
            x=x+1
            mylist.append(x)
            key = x+5
            mydict[key]= 1
        print "my_function is done!"
 

process = multiprocessing.Process(target=my_function)
process.start()
# # process.join()

    # x=999
    # while(x>990):
    #     print x
    #     print mylist
    #     time.sleep(2)
    #     x = x-1
while True:
    print 'mylist: ',mylist
    print 'mydict: ',mydict

    # if len(mylist)>0:
    #     print 'mylist[0]',mylist[0]
    
    mydict.pop(8,0)


print "__main__ is done!"



# import time
# import multiprocessing
# from multiprocessing import Process, Value, Array, Manager

# mylist = Manager().list()
# mydict = Manager().dict()
 
# def my_function():
#     # time.sleep(3)
#     x=0
#     while(x<100):
#         print x
#         time.sleep(1)
#         x=x+1
#         mylist.append(x)
#         key = x+5
#         mydict[key]= 1
#     print "my_function is done!"
 

# process = multiprocessing.Process(target=my_function)
# process.start()
# # process.join()

#     # x=999
#     # while(x>990):
#     #   print x
#     #   print mylist
#     #   time.sleep(2)
#     #   x = x-1
# while True:
#     time.sleep(2)
#     print 'mylist: ',mylist
#     print 'mydict: ',mydict

print "__main__ is done!"
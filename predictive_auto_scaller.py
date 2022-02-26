#new2
#predictive_auto_scaller:

#new2


def predictive_autoscalling(y_axis, number_of_records):
  import numpy as np
  print("Before prediction Time is : ",datetime.now().strftime("%H:%M:%S"))
  from sklearn.linear_model import LinearRegression
  time = list()
  count = 1
  while count <= number_of_records:
    time.append(count)
    count += 1
  

  #converting time and cpu to numpy for finding model x, y 
  x = np.array(time).reshape((-1, 1))
  y = y_axis #picking last 10 records from cpu and making there numpy array

  # print("x.shape: ", x.shape)
  # print("y.shape: ", y.shape)

  # print("x: ", x)
  # print("y: ", y)
  
  #going to fit the linear model
  model = LinearRegression().fit(x, y)

  #going to predict the linear model

  predicted_cpu = int(model.predict([[number_of_records+1]]))

  #print("predicted_cpu: ",predicted_cpu)
  
  print("After prediction Time is : ",datetime.now().strftime("%H:%M:%S"))

  return predicted_cpu




#---------------------------------------------------------------------------------------------
def calculate_y_axis(running_pods_list, number_of_records, address):  #(like list of 3 frontends, last 10 records, directory address where these frontend are placed)
  import numpy as np
  import pandas as pd
  average_of_pods_cpu = list()

  np_array = np.zeros((1,number_of_records))

  #print("np_array shape1: ",np_array.shape,"\n",np_array)

  for i in running_pods_list:
    cpu_list = list()
    #print("i: ",i)
    
    trn_data = pd.read_csv(address+i)

    no_of_records_in_pod_file = len(trn_data)    #no_of_records_in_a particular pod file

    if no_of_records_in_pod_file > number_of_records:
      cpu_list.append(trn_data.iloc[:,1].tail(number_of_records)) #select second column(cpu) and last 10 rows 
    else:
      count = number_of_records - no_of_records_in_pod_file  # it will tell how many records are less then our window sent like 10 - 2 = 8 are missing and now we will append 8 zeros at start to make numpy shape equal 
      count2 = 1
      while count2 <= count:
        count2 +=1
        cpu_list.append(0)

      # going to get the taling values from cpu clumn and will add them into cpu_list
      cup_taling_values = trn_data.iloc[:,1].tail(no_of_records_in_pod_file)
      for i in cup_taling_values:
        cpu_list.append(i) # it will append no_of_records_in_pod_file cpu values at end of cpu_list
      
    # print("\n")
    # print("cpu_list: \n",cpu_list)
    # print("\n")

    # for i in cpu_list:
    #   print("i:",i)


    np_array = np.vstack([np_array, cpu_list])   #it will append new cpu list to the numpy array
    #np_array = np.append(np_array, cpu_list, axis=1))

  #print("np_array shape2: ",np_array.shape,"\n",np_array)
  #print("np_array shape2: ",np_array.shape[0]) # it will print the number of records in numpy array

  #print("/len(np_array): ",len(np_array))

  y_axis = (np.sum(np_array, axis=0))

  print("y_axis: ",y_axis)
  print("np_array.shape[0]: ",np_array.shape[0])
  average_y_axis = y_axis/(np_array.shape[0]-1)  #it will devide the every element of the list with number of records in numpy array (it will give the average value)

  print("average_y_axis: ",average_y_axis)
  return average_y_axis


#---------------------------------------------------------------------------------------------
#file_list = it contain multiple running pods


def cpuusage(time, podname, running_pods_list):
  import pandas as pd

  count = 0
  cpu = 0

  print("\nrunning_pods_listlllll: ",running_pods_list)

  for i in running_pods_list:
    if os.path.isfile(address+i):
      print ("File exist ")
      
    trn_data = pd.read_csv(address+i)
    last_cpu = trn_data.iloc[:,1].tail(1) # it will give the last cpu value of every frontend etc
    print("last_cpu: ",last_cpu)
    last_cpu = float(str(last_cpu).split(" ")[4].split("\n")[0])
    #print("last_cpu: ",last_cpu)
    cpu = cpu + last_cpu

    count += 1

  #print("cpu: ",cpu)
  

  cpu = cpu/count # it will give the average cpu value of specific pod

  #print (time," ",podname," ",cpu)
  f = open("poddata/cpuusage.txt", "a")  
  f.write(f"{time},{podname},{cpu}\n")
  f.close()

#---------------------------------------------------------------------------------------------

def finding_y_axis(number_of_records, address):
  from datetime import datetime
  import os
  #creating running pods file
  #subprocess.call("./running_pods_finder.sh")
  os.system(f"./running_pods_finder.sh")

  checked_pods = list() #pods that are onced checked in one cycle
  #pods_that_are_going_to_check = list()

  
  
  file_list=os.listdir(address) # it will return list of directories name in a particular address

  for i in file_list:
    pod_name = i.split('-')[0] # it will give just frontend and remove everything else from it
    
    # print("\npod_name: ",pod_name)

    if pod_name not in checked_pods:
      checked_pods.append(pod_name)

      running_pods = open('multiple_running_pods.txt').readlines()  # it will give the list of running pods

      running_pods_list = list()   #it contain like how many frontend replicas are running

      for j in running_pods:
        # print("j1: ",j," pod_name: ",pod_name)
        if pod_name in j:   #frontend in frontendxkdwij.csv
          j = j.split('\n')[0]  # it will remove \n from the end of the name of file
          # print("j: ",j)
          if j not in running_pods_list:
            running_pods_list.append(j)

      #print("\nrunning_pods_list: ",running_pods_list)

      # ..................

      if len(running_pods_list) >= 1:

        cpuusage(datetime.now().strftime("%H:%M:%S"),pod_name,running_pods_list)#-------------------------<<<<<<<<<<<<<<<

        print("\nrunning_pods_list: ",running_pods_list, len(running_pods_list))

        y_axis = calculate_y_axis(running_pods_list, number_of_records, address)

        #print("back: ",y_axis.shape,"\n",y_axis)

        predicted_cpu = predictive_autoscalling(y_axis, number_of_records)

        print("\npredicted_cpu: ",predicted_cpu)

        
        #print("pod_name: ",pod_name)
        
        

        os.system(f"./replicas_set_getter.sh "+str(pod_name))  #pod_name = frontend
        

        if predicted_cpu > 80:      

          f = open("current_replics.txt", "r")
          no_of_replicas = int(f.read())
          # print("content: ",no_of_replicas)
          no_of_replicas += 1
          os.system(f"kubectl scale -n default deployment "+str(pod_name)+" --replicas="+str(no_of_replicas))

          print("time: ",datetime.now().strftime("%H:%M:%S"), " scall up: ",pod_name)

        elif predicted_cpu < 50 and predicted_cpu > 1: 

          f = open("current_replics.txt", "r")
          no_of_replicas = int(f.read())
          # print("content: ",no_of_replicas)
          if no_of_replicas > 1:
            no_of_replicas -= 1
            os.system(f"kubectl scale -n default deployment "+str(pod_name)+" --replicas="+str(no_of_replicas))

          print("time: ",datetime.now().strftime("%H:%M:%S"), " scall down: ",pod_name, " number of replicas: ",no_of_replicas)

        

  print("\ngoing back\n")

  
  os.system(f"rm multiple_running_pods.txt")  #removing the multiple_running_pods.txt



#----------------------------------
def podmaker(address):
  from csv import writer
  from datetime import datetime

  count = 1
  l = []

  data = open(address+"podcollector.txt", 'r')
  Lines = data.readlines()

  for i in Lines:  
    j = i.split(' ')

    if ('NAME' or 'CURRENT') not in j:      
      #l2.append(j[0].split('-')[0]) #it is use to get the service name like frontend
      l.append(j[1].split('\n')[0]) #it will select second column that have cpus of different services. then it will select first column from that second column that will remove \n from the end
      count +=1
      
      if count == 12:
        l.append(datetime.now().strftime("%D,%H:%M:%S")) #it will print the date and time at the end of list
        with open(address+'poddata/poddata.csv', 'a') as f_object:
          writer_object = writer(f_object)
          writer_object.writerow(l)
          f_object.close()
        l = []      
        count = 1

#----------------------------------

def cpuusage_reactive(number_of_records, address):   #----------<<<<<<<<1
  from datetime import datetime
  import os
  #creating running pods file
  #subprocess.call("./running_pods_finder.sh")
  os.system(f"./running_pods_finder.sh")

  checked_pods = list() #pods that are onced checked in one cycle
  #pods_that_are_going_to_check = list()

  
  
  file_list=os.listdir(address) # it will return list of directories name in a particular address

  for i in file_list:
    pod_name = i.split('-')[0] # it will give just frontend and remove everything else from it
    
    # print("\npod_name: ",pod_name)

    if pod_name not in checked_pods:
      checked_pods.append(pod_name)

      running_pods = open('multiple_running_pods.txt').readlines()  # it will give the list of running pods

      running_pods_list = list()   #it contain like how many frontend replicas are running

      for j in running_pods:
        # print("j1: ",j," pod_name: ",pod_name)
        if pod_name in j:   #frontend in frontendxkdwij.csv
          j = j.split('\n')[0]  # it will remove \n from the end of the name of file
          # print("j: ",j)
          if j not in running_pods_list:
            running_pods_list.append(j)
          

      #print("\nrunning_pods_list: ",running_pods_list)

      # ..................

      if len(running_pods_list) >= 1:

        cpuusage(datetime.now().strftime("%H:%M:%S"),pod_name,running_pods_list)#-------------------------<<<<<<<<<<<<<<<


#---------------------------------

if __name__ == '__main__':
  from csv import writer
  import time
  import os
  import os.path
  from datetime import datetime
 
  number_of_records = 10
  address = "/home/ubuntu/umer/clustor-stats10005/"

  l2 = ['adservice', 'cartservice', 'checkoutservice', 'currencyservice', 'emailservice', 'frontend', 'paymentservice', 'productcatalogservice', 'recommendationservice', 'redis', 'shippingservice', 'time']
  
  with open(address+'poddata/poddata.csv', 'w') as f_object:    
    writer_object = writer(f_object)
    writer_object.writerow(l2)
    f_object.close()

  while True:

    cpuusage_reactive(int(number_of_records), address) #----------<<<<<<<<1

    os.system(f"./reactive_autoscaller.sh")
    #it is use to check which technique will apply reactive or predictive
    os.system(f"temp=`cat file_names.txt | head -1` && cat $temp | wc -l > pod_files_line_count.txt")
    f = open("pod_files_line_count.txt", "r")
    line_count = int(f.read())
    print("line_count: ",line_count)

    os.system(f"./podcollector.sh")
    podmaker(address)

    time.sleep(30)
    if line_count > 10:
      break
# print("Allah Hafiz")
  print("going to apply predictive auto scalling")
  while True:
    os.system(f"./podcollector.sh") # it will tell how many pods are currently running 
    podmaker(address)

    finding_y_axis(int(number_of_records), address)
    
    time.sleep(30)

    
  


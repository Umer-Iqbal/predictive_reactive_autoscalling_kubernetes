#bash code

#!/bin/bash
get_file_names()
{
    ls -al | grep .csv | awk '{print $9}' > file_names.txt
}

multiple_running_pods_txt_file_maker()  #this funcation is use to pick only alive pods file to perform operation
{
    while read podname;
    do
        filename_of_pod=$podname #(like frontend-85-85.csv)
        podname=`echo $podname | cut -f1 -d"."` #(remove .csv from end)

        kubectl get pods | awk '{print $1}' > kgp.txt    #it will give the name of all the running pods

        while read kgp_podname;
        do
            if [ "$podname" = "$kgp_podname" ]
            then               
                echo $filename_of_pod >> multiple_running_pods.txt               
                
            fi           

        done < kgp.txt       

        rm kgp.txt

    done < file_names.txt
}


get_file_names  #funcation calling
multiple_running_pods_txt_file_maker    #it will make multiple_running_pods.txt file (it is a funcation calling)



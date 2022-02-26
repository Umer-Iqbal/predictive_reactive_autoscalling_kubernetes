#!/bin/bash
echo "podname: $1" 
kubectl get rs | grep $1 | awk '{print $3}' > current_replics.txt  #pod_name = frontend


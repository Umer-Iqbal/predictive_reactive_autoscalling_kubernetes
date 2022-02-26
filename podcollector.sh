kubectl get rs | awk '{print $1, $3}' >podcollector.txt
kubectl get rs | awk '{print $1, $3}' >>podcollector2.txt

import ast
import csv
import re
import Crypto

print(Crypto.__file__)
import time
from datetime import datetime

import paramiko
import os
import subprocess
from threading import Thread


class GetPodsData(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.json_attr = """-o=jsonpath="{"["}{range .items[*]}{"["}{"'"}{.status.hostIP}{"'"}{","}{"'"}{.metadata.name}{"'"}{","}{"'"}{range .status.containerStatuses[*]}{.containerID}{"'"}{"]"}{","}{end}{end}{"]"}" """

        self.cmd = ["kubectl", "get", "pods", self.json_attr]
        self.all_pods = []
        self.new_pods = []
        self.start()

    def run(self):
        # while True:
            cmd = subprocess.Popen(self.cmd, stdout=subprocess.PIPE)
            out, err = cmd.communicate()
            if out:
                pods_list = ast.literal_eval(ast.literal_eval(out.decode()))
                self.new_pods = [pod for pod in pods_list if pod not in self.all_pods]

                print("Starting main thread " + str(self.new_pods))
                self.all_pods = self.all_pods + self.new_pods

            # time.sleep(5)


class GetPodStats(Thread):
    def __init__(self, pod):
        Thread.__init__(self)
        self.daemon = True
        self.cmd = """docker stats {container_id} --format "{{{{.CPUPerc}}}},{{{{.MemUsage}}}},{{{{.MemPerc}}}},{{{{.NetIO}}}},{{{{.BlockIO}}}}" --no-stream"""
        self.pod = pod
        self.num_regex = re.compile(r"\d+\.?\d*")
        self.hosts_user_map = {
            "192.168.1.201": "worker@192.168.1.201",
            "192.168.1.205": "worker5@192.168.1.205"
        }
        self.start()

    def run(self):

        ml_api_pods = 1
        time_to_scale = 7

        host = self.hosts_user_map.get(self.pod[0])
        pod_name = self.pod[1]

        if "fft" in pod_name:
            exit(0)
        container_id = self.pod[2].split('/')[-1][:12]
        print("umer")
        print(f"Starting thread for {pod_name} and {host.split('@')[0]} and {host.split('@')[1]}")

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=host.split('@')[1], username=host.split('@')[0], password='abdullah',
                           allow_agent=False, look_for_keys=False)

        # arteration11=1
        # while arteration11 <= 100:
        while True:
            # arteration11 +=1

            stdin, stdout, stderr = ssh_client.exec_command(self.cmd.format(container_id=container_id))

            output = stdout.readlines()

            if output:
                print(output)
                raw_stats = output[0].split(",")
                raw_stats = [i.split("/") for i in raw_stats]

                stats = [datetime.now().strftime("%H:%M:%S")] + \
                        [self.num_regex.findall(item)[0] for sublist in raw_stats for item in sublist]

                with open(pod_name + ".csv", "a") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(stats)

            time.sleep(30)
            time_to_scale += 1


if __name__ == '__main__':
    get_pods_data = GetPodsData()
    while True:
        for pod in get_pods_data.new_pods:
            GetPodStats(pod)
            get_pods_data.new_pods.remove(pod)

import random
import sys
import time
import masscan
from mcstatus import JavaServer
import json
import os
import math
import threading
import time
import argparse


def split_array(L, n):
    return [L[i::n] for i in range(n)]


def ipToId(ip):
    id = ip.replace(".", "0")
    return id



class myThread (threading.Thread):
    def __init__(self, threadID, ip):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = ip

    def run(self):
        print("Starting Thread " + self.name)
        print_time(self.name)
        print("Exiting Thread " + self.name)


exitFlag = 0


def print_time(threadName):
    if exitFlag:
        threadName.exit()
    try:
        ip = threadName
        server = JavaServer(ip, 25565)
        status = server.status()
    except:
        print("Failed to get status of: " + ip)
    else:
        print("Found server: " + ip + " " + status.version.name +
              " " + str(status.players.online))
        playersString = "Palyer:"
        if status.players.sample is not None:
            for player in status.players.sample:
                playersString += " "
                playersString += player.name
        print(playersString)


if __name__ == "__main__":

    # threads = int(
    #     input('How many threads do you want to use? (Recommended 20): '))

    # create IP ranges
    A = list(range(1, 0xff))
    B = list(range(1, 0xff))
    random.shuffle(A)
    random.shuffle(B)
    ip_ranges = []
    for a in A:
        for b in B:
            ip_range = f"{a}.{b}.0.0/16"
            ip_ranges.append(ip_range)

    while True:
        random.shuffle(ip_ranges)
        for ip_range in ip_ranges:
            print(ip_range)
            try:
                mas = masscan.PortScanner()
                mas.scan(ip_range, ports='25565',
                         arguments='--max-rate 300000 --excludefile exclude.conf')
                scan_result = json.loads(mas.scan_result)
                # print(scan_result["scan"])
                scanJobs = []
                for ip in scan_result["scan"]:
                    host = scan_result["scan"][ip]
                    if "tcp" == host[0]["proto"] and 25565 == host[0]["port"]:
                        scanJobs.append(ip)
                        # try:
                        #     server = JavaServer(ip, 25565)
                        #     status = server.status()
                        #     print("Server:")
                        #     print(f"Desc: {status.description}")
                        #     print(f"IP: {ip}")
                        #     print(
                        #         f"PalyerCount: {status.players.online}/{status.players.max}")
                        #     playersString = "Palyer:"
                        #     for player in status.players.sample:
                        #         playersString += " "
                        #         playersString += player.name
                        #     print(playersString)
                        #     print(
                        #         f"Version: {status.version.protocol} {status.version.name}")
                        #     print("-----")
                        # except:
                        #     print("Failed to get status of: " + ip)
                    thread = myThread(ipToId(ip), ip).start()

            except OSError:
                print(f"{ip_range} masscan error")
        print("done scanning")

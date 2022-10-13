import random
import masscan
from mcstatus import JavaServer
import json
import threading
import queue
import requests
import time


ipQ = queue.LifoQueue()
ipQ.maxsize = 150
sendQ = queue.LifoQueue()
sendQ.maxsize = 300


class sendThread (threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = threadID

    def run(self):
        print("Starting Thread " + self.name)
        while True:
            serverSend = sendQ.get()
            try:
                url = 'https://api.gamingformiau.de/api/mcscanner'
                response = requests.post(url, json=serverSend)
                print(response.status_code)
                if (response.status_code != 200):
                    print("Failed to send")
            except:
                print("Failed to send")


class scanThread (threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = threadID

    def run(self):
        print("Starting Thread " + self.name)
        while True:
            print_time(self.name, ipQ.get())


exitFlag = 0


def print_time(threadName, ip):
    if exitFlag:
        print("Exiting Thread " + threadName)
        threadName.exit()
    try:
        server = JavaServer(ip, 25565)
        status = server.status()
    except:
        print("Failed to get status of: " + ip)
    else:
        print("Found server: " + ip + " " + status.version.name +
              " " + str(status.players.online))
        players = []
        if status.players.sample is not None:
            for player in status.players.sample:
                players.append({'id': player.id,
                               'name': player.name})
        serverScan = {'players': players,
                      'ip': ip,
                      'desc': status.description,
                      'maxPlayer': status.players.max,
                      'versionProtocol': status.version.protocol,
                      'versionName': status.version.name
                      }
        print(serverScan)
        sendQ.put(serverScan)


if __name__ == "__main__":

    threads = int(
        input('How many threads do you want to use? (Recommended 20): '))

    for i in range(threads):
        scanThread(i).start()
    sendThread(threads + 1).start()

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
            print(f"{ip_range} Check queue: {ipQ.qsize()}")
            try:
                mas = masscan.PortScanner()
                mas.scan(ip_range, ports='25565',
                         arguments='--max-rate 300000 --excludefile exclude.conf')
                scan_result = json.loads(mas.scan_result)
                # print(scan_result["scan"])
                # scanJobs = []
                for ip in scan_result["scan"]:
                    host = scan_result["scan"][ip]
                    if "tcp" == host[0]["proto"] and 25565 == host[0]["port"]:
                        # scanJobs.append(ip)
                        ipQ.put(ip)
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

            except OSError:
                print(f"{ip_range} masscan error")
        ipQ.join()
        print("done scanning")

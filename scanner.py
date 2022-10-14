import random
import masscan
from mcstatus import JavaServer
import json
import threading
import queue
import requests
import time

ipPortQ = queue.LifoQueue()
sendQ = queue.LifoQueue()


class sendThread(threading.Thread):

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
                if (response.status_code != 200
                        and response.status_code != 500):
                    sendQ.put(serverSend)
                    print(f"Failed to send:\n{serverSend}\nWaititing 30 sec")
                    time.sleep(30)
            except:
                sendQ.put(serverSend)
                print(f"Failed to send:\n{serverSend}\nWaititing 30 sec")
                time.sleep(30)


class scanThread(threading.Thread):

    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = threadID

    def run(self):
        print("Starting Thread " + self.name)
        while True:
            print_time(self.name, ipPortQ.get())


exitFlag = 0


def print_time(threadName, ipPort):
    ip = str(ipPort["ip"])
    port = str(ipPort["port"])

    if exitFlag:
        print("Exiting Thread " + threadName)
        threadName.exit()
    try:
        server = JavaServer(ip, port)
        status = server.status()
    except:
        print("Failed to get status of: " + ip + ":" + port)
    else:
        print("Found server: " + ip + ":" + port + " " + status.version.name +
              " " + str(status.players.online))
        players = []
        if status.players.sample is not None:
            for player in status.players.sample:
                players.append({'id': player.id, 'name': player.name})
        ipPortString = ip + ":" + port
        serverScan = {
            'players': players,
            'ip': ipPortString,
            'desc': status.description,
            'maxPlayer': status.players.max,
            'versionProtocol': status.version.protocol,
            'versionName': status.version.name
        }
        print(serverScan)
        sendQ.put(serverScan)


if __name__ == "__main__":

    threads = int(
        input('How many threads do you want to use? (Recommended 100): '))

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
        for i in range(len(ip_ranges)):
            progress = round(i / len(ip_ranges) * 100)
            print(
                f"IpRange: {ip_ranges[i]} | Progress: {progress}% | Check queue: {ipPortQ.qsize()} | Send queue: {sendQ.qsize()}"
            )
            try:
                mas = masscan.PortScanner()
                mas.scan(
                    ip_range,
                    ports=
                    '25565,25566,25567,25568,25569,25570,25571,25572,25573,25574,25575,25576,25577',
                    arguments='--max-rate 300000 --excludefile exclude.conf')
                scan_result = json.loads(mas.scan_result)
                print(scan_result["scan"])
                for ip in scan_result["scan"]:
                    host = scan_result["scan"][ip]
                    if "tcp" == host[0]["proto"] and 25565 == host[0]["port"]:
                        ipPortQ.put({"ip": ip, "port": host[0]["port"]})

            except OSError:
                print(f"{ip_range} masscan error")
        ipPortQ.join()
        print("done scanning")

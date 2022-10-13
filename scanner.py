import random
import sys
import time
import masscan
from mcstatus import JavaServer
import json


if __name__ == "__main__":

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
                print(scan_result["scan"])
                for ip in scan_result["scan"]:
                    print(ip)
                    host = scan_result["scan"][ip]
                    print(f"Found: {ip} {host}")
                    print(host[0]["port"])
                    print(host[0]["proto"])
                    if "tcp" is host[0]["proto"] and 25565 is host[0]["port"]:
                        print("if true")
                        try:
                            server = JavaServer(ip, 25565)
                            status = server.status()
                            print(status)
                        except:
                            print("Failed to get status of: " + ip)

            except OSError:
                print(f"{ip_range} masscan error")
            print("-----")
        print("done scanning")

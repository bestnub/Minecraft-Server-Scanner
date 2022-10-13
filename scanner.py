import random
import time
import masscan
from mcstatus import JavaServer


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
            # try:
            mas = masscan.PortScanner()
            mas.scan(ip_range, ports='25565',
                         arguments='--max-rate 300000 --excludefile exclude.conf')
            print("eval")
            for ip in mas.scan_result['scan']:
                host = mas.scan_result['scan'][ip]
                print(f"{ip} {host}")
                if 'tcp' in host and 25565 in host['tcp']:
                    try:
                        server = JavaServer(ip, 25565)
                        status = server.status()
                        print(status)
                    except:
                        print("Failed to get status of: " + ip)

            # except:
                # print(f"{ip_range} masscan error")
            time.sleep(30)
        print("done scanning")
